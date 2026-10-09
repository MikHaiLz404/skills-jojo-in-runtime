# External skill sources

This directory records skills that are useful locally but are not distributed
by the private Emily marketplace. Their attribution, license status, and
upstream remain authoritative; they must not be rebranded as Emily work.

`sources.json` is the tracked registry. Optional local working copies live in
`external/checkouts/`, which is deliberately ignored by Git. To update a
checkout, use its own upstream, for example:

```sh
git -C external/checkouts/caveman pull --ff-only
```

That refreshes only the local external reference. It neither changes nor
updates the Emily marketplace catalog.
