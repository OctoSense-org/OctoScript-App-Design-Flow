//! Lightweight wrapper for CPU-bound tasks.
//!
//! Jobs use the shared Makepad heavy-work lane. Refused jobs are retried
//! on a later UI event without blocking rendering.

use makepad_widgets::Cx;
use std::sync::{atomic::AtomicBool, mpsc::Sender, Arc};
use crate::{
    room::member_search::{self, search_room_members_streaming_with_sort, PrecomputedMemberSort},
    shared::mentionable_text_input::SearchResult,
    sliding_sync::TimelineKind,
};
use matrix_sdk::room::RoomMember;

pub enum CpuJob {
    SearchRoomMembers(SearchRoomMembersJob),
    PrecomputeMemberSort(PrecomputeMemberSortJob),
}

/// Action posted back to UI thread when precomputed sort is ready.
#[derive(Debug)]
pub struct PrecomputedMemberSortReady {
    pub timeline_kind: TimelineKind,
    pub sort: Arc<PrecomputedMemberSort>,
    /// The Arc<Vec<RoomMember>> this sort was computed for.
    /// Held alive to prevent ABA via address reuse; compared by Arc::ptr_eq.
    pub members_arc: Arc<Vec<RoomMember>>,
}

pub struct PrecomputeMemberSortJob {
    pub timeline_kind: TimelineKind,
    pub members: Arc<Vec<RoomMember>>,
}

pub struct SearchRoomMembersJob {
    pub members: Arc<Vec<RoomMember>>,
    pub search_text: String,
    pub max_results: usize,
    pub sender: Sender<SearchResult>,
    pub search_id: u64,
    pub precomputed_sort: Option<Arc<PrecomputedMemberSort>>,
    pub cancel_token: Option<Arc<AtomicBool>>,
}

fn run_member_search(params: SearchRoomMembersJob) {
    let SearchRoomMembersJob {
        members,
        search_text,
        max_results,
        sender,
        search_id,
        precomputed_sort,
        cancel_token,
    } = params;

    search_room_members_streaming_with_sort(
        members,
        search_text,
        max_results,
        sender,
        search_id,
        precomputed_sort,
        cancel_token,
    );
}

fn run_precompute_sort(params: PrecomputeMemberSortJob) {
    let sort = member_search::precompute_member_sort(&params.members);
    Cx::post_action(PrecomputedMemberSortReady {
        timeline_kind: params.timeline_kind,
        sort: Arc::new(sort),
        members_arc: params.members, // keep alive to prevent ABA
    });
}

/// Submit a CPU-bound job to the shared framework pool.
pub fn spawn_cpu_job(cx: &mut Cx, job: CpuJob) {
    crate::cpu_worker::spawn_background_job(cx, move || match job {
        CpuJob::SearchRoomMembers(params) => run_member_search(params),
        CpuJob::PrecomputeMemberSort(params) => run_precompute_sort(params),
    });
}

/// Run blocking work on the framework's shared pool, retaining a refused job
/// on the UI thread until a later event makes a queue slot available.
#[derive(Default)]
struct PendingJobs(std::collections::VecDeque<Box<dyn FnOnce() + Send>>);

pub fn spawn_background_job(cx: &mut Cx, job: impl FnOnce() + Send + 'static) {
    cx.global::<PendingJobs>().0.push_back(Box::new(job));
    pump_background_jobs(cx);
}

pub fn pump_background_jobs(cx: &mut Cx) {
    use makepad_widgets::makepad_platform::thread::Lane;
    let pool = cx.task_pool();
    loop {
        let Some(job) = cx.global::<PendingJobs>().0.pop_front() else { break; };
        match pool.try_submit(Lane::Heavy, job) {
            Ok(handle) => handle.detach(),
            Err(refused) => {
                cx.global::<PendingJobs>().0.push_front(refused.job);
                cx.new_next_frame();
                break;
            }
        }
    }
}
