# github-graveyard

A tiny self-growing graveyard for GitHub repositories you have not touched in a while.

Repositories become tombstones based on their real `pushed_at` date. Time grows the vegetation: after 30 days grass appears, after 90 days it gets thicker, after 180 days vines arrive, and after a year the place is properly ancient. Push to a repository again and it digs itself back out on the next run.

![example graveyard](./examples/graveyard.svg)

## use it

Copy `graveyard.py` and the workflow into your profile repository, then add `<img src="./graveyard.svg" width="100%" alt="My repository graveyard" />` to the README. The workflow runs daily and can also be triggered manually. No third-party dependencies are required.

Run locally with `python graveyard.py --user YOUR_GITHUB_NAME --output graveyard.svg`. Options: `--minimum-days 30` controls burial age and `--limit 8` controls cemetery capacity. Forks, archived repositories, and the profile repository itself are ignored.

## vegetation

| silence | condition |
| --- | --- |
| 30+ days | grass |
| 90+ days | overgrown |
| 180+ days | vines |
| 365+ days | ancient vines |

MIT. Please treat the gravekeeper kindly.
