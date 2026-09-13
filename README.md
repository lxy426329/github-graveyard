# github-graveyard

A tiny self-growing graveyard for GitHub repositories you have not touched in a while.

Repositories become tombstones based on their real `pushed_at` date. Time grows the vegetation: after 30 days grass appears, after 90 days it gets thicker, after 180 days vines arrive, and after a year the place is properly ancient. Push to a repository again and it digs itself back out on the next run.

![example graveyard](./examples/graveyard.svg)

## use it

Use `lxy426329/github-graveyard@v0.6.0` from a scheduled workflow in your profile repository, then add `<img src="./graveyard.svg" width="100%" alt="My repository graveyard" />` to the README. The workflow runs daily and can also be triggered manually. No third-party dependencies are required.

Run locally with `python graveyard.py --user YOUR_GITHUB_NAME --output graveyard.svg`. Options: `--minimum-days 30` controls burial age and `--limit 8` controls cemetery capacity. Forks and the profile repository itself are ignored. Archived repositories can be shown as clean memorials.

## vegetation

| silence | condition |
| --- | --- |
| 30+ days | grass |
| 90+ days | overgrown |
| 180+ days | vines |
| 365+ days | ancient vines |

MIT. Please treat the gravekeeper kindly.


## configure the cemetery

Choose what is visible with `mode`: `all` shows inactive graves and archived memorials, `inactive` hides archived projects, and `archived` shows only deliberately finished/archived projects. The last option is useful if you do not want unfinished work exposed.

Choose the footprint with `rows: 1` (four graves), `rows: 2` (eight graves), and so on. `rows` overrides `limit`. Hide individual repositories with a comma-separated `exclude`, for example `exclude: secret-project,still-alive`.

Archived projects are laid to rest cleanly: a small memorial flower, no weeds, and no quiet-days counter. They do not participate in resurrection history.

For reliable GitHub Profile navigation, set `links-output: graveyard-links.md`; this creates ordinary clickable Markdown links for the graves currently shown.

```yaml
- uses: lxy426329/github-graveyard@v0.6.0
  with:
    user: YOUR_GITHUB_NAME
    mode: all          # all | inactive | archived
    rows: '1'
    exclude: ''
    links-output: graveyard-links.md
```
