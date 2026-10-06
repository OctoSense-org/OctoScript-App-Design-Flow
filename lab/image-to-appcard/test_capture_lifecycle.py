import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import studio


class CaptureLifecycleTests(unittest.TestCase):
    def test_screenshot_crops_viewport_and_preserves_raw_pixels(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);source=p/'studio.png'
            pixels=Image.new('RGB',(12,20),(17,31,47));pixels.putpixel((7,11),(251,101,5));pixels.save(source)
            receipt=studio.save_viewport_screenshot({'path':str(source),'width':12,'height':20,'build_id':[7]},p/'native.png',4,6,2)
            with Image.open(p/'native.png') as actual:
                self.assertEqual(actual.size,(8,12));self.assertEqual(actual.getpixel((7,11)),(251,101,5))
            self.assertEqual((p/'native-raw.png').read_bytes(),source.read_bytes())
            self.assertEqual(receipt['crop_xywh'],[0,0,8,12]);self.assertFalse(receipt['resampled'])

    def test_launch_redirects_every_output_away_from_archived_round(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);old=root/'rounds/001';old.mkdir(parents=True)
            archive=old/'native.json';archive.write_text('immutable evidence')
            request={'card':'page.card','data':'page.data.json','result':str(archive),'layout':str(old/'layout.json'),
                     'actions':str(old/'actions.json'),'semantic_result':str(old/'semantic-state.json'),'semantic_probe':str(old/'probe.json')}
            (root/'current-request.json').write_text(json.dumps(request))
            def remote(kind,*args):
                return {'builds':[]} if kind=='ListBuilds' else {'build_id':[999]}
            with patch.object(studio,'HERE',root),patch.object(studio,'request',side_effect=remote):studio.launch()
            current=json.loads((root/'current-request.json').read_text())
            for key in ('result','layout','actions','semantic_result','semantic_probe'):
                self.assertTrue(Path(current[key]).is_relative_to(root/'qa-work/startup'))
            self.assertEqual(archive.read_text(),'immutable evidence')
    def test_interaction_cannot_rewrite_an_already_gated_round(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);(p/'gate.json').write_text('{}')
            with self.assertRaisesRegex(ValueError,'immutable'):studio.click_controls(p,[1])

    def test_disabled_button_requires_disabled_native_state_and_no_activation(self):
        for native_enabled,activated,expected in [(False,False,True),(True,False,False),(False,True,False)]:
            with self.subTest(native_enabled=native_enabled,activated=activated),tempfile.TemporaryDirectory() as td:
                p=Path(td)/'rounds/001';p.mkdir(parents=True)
                node={'kind':'button','source_id':'confirm','native_id':'beauty_0_1',
                      'bounds':[10,20,100,40],'enabled':0,'parent':'surface'}
                for name,data in {'mapping.json':{'elements':[node]},'semantic-map.json':{'elements':[]},
                                  'actions.json':[],'provenance.json':{'nonce':'disabled-probe'}}.items():
                    (p/name).write_text(json.dumps(data))
                def remote(kind,body,response=None):
                    if kind=='Click' and activated:
                        (p/'actions.json').write_text(json.dumps([{'id':'surface','action':{'kind':'activated'}}]))
                    if kind=='WidgetSnapshot':
                        return {'build_id':[1],'widgets':[{'id':'beauty_0_1','enabled':native_enabled}]}
                    return {'build_id':[1],'query':'id:beauty_0_1','rects':[[10,20,100,40]]}
                with patch.object(studio,'request',side_effect=remote),patch.object(studio.time,'monotonic',side_effect=[0,.1,1]),patch.object(studio.time,'sleep'):
                    studio.click_controls(p,[1])
                result=json.loads((p/'interactions.json').read_text())
                self.assertEqual(result['pass'],expected)

    def test_progress_probe_waits_for_requested_value_and_paint_on_restore(self):
        before={'before':.3,'after':.75,'value':.75,'painted_value':.75}
        samples=[
            {**before,'painted_value':.3},  # late paint from the preceding probe
            {'before':.75,'after':.3,'value':.3,'painted_value':.75},
            {'before':.75,'after':.3,'value':.3,'painted_value':.3},
        ]
        read=iter({'elements':{'progress':s}} for s in samples)
        with patch.object(studio.time,'sleep') as sleep:
            result=studio.await_semantic_change(lambda:next(read),'progress',before,.3,paint=True)
        self.assertEqual(result,samples[-1]);self.assertEqual(sleep.call_count,2)

    def test_unsettled_probe_fails_instead_of_publishing_stale_state(self):
        with patch.object(studio.time,'monotonic',side_effect=[0,6]):
            with self.assertRaisesRegex(RuntimeError,'did not settle for progress'):
                studio.await_semantic_change(lambda:{'elements':{}},'progress',{},.3,paint=True)


if __name__=='__main__':unittest.main()
