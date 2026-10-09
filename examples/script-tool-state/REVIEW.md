# Development review

English | [简体中文](REVIEW.zh-CN.md)

Author self-review, not Hub administrator approval. Native acceptance status
is recorded in the README and validation receipt; declarations alone do not pass.

1. The source calls itself “Script Tool State”. UI and tools call the same
   `apply` function, which checks storage success before reporting a saved revision.
2. Only macOS is claimed for this developer/productivity fixture; phone and
   other platforms are unverified.
3. Only `storage` is requested. No network, account, model or OS-device method
   is called. `script-tools-v1` is a compatibility requirement, not a permission.
4. The UI is an editor with a save action; it imitates no host approval or login.
5. `AGENT.md` contains the declared assistant guidance. The ordinary UI contains
   no prompt-like external content, and the fixture reads no external data.
6. Test topics are synthetic and target no private individual.
7. Development acceptance and publication differ: public submission needs its
   own human review. No published replacement for a contestant's app is claimed.
8. The optional assistant has one read tool and one local action tool. Both
   declare private data, disallow sharing, and use bounded schemas. They run in
   the open app, not in a hidden worker. The native test does not prove consent
   or peer routing; real agent requests still pass those host checks.
