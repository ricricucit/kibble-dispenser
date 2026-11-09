# Product lock file

`product.json` describes the sellable kit, the Kibble Dispenser Outdoor, as one version that pins everything in it. It is the source of truth of the product version line (tag `product-vX.Y.Z`, see [VERSIONS.md](../VERSIONS.md)).

**Status: unreleased.** There is no product release yet. The first one, `product-v1.0.0`, will pin a hardware release with the status tested and a firmware release that has run on it.

## Fields

- `version`: the product version, or `"unreleased"`. The release workflow only tags a product when this is a version.
- `date`: the release date (YYYY-MM-DD).
- `hardware.tag`: the pinned hardware release, for example `"hw-v6.1.0"`. `hardware.required_status` lists the hardware statuses a product may ship with.
- `firmware.tag`: the pinned firmware release, for example `"fw-v1.0.0"`.
- `manual.version` and `manual.file`: the manual that goes with the kit (a PDF in the repository).
- `bom`: the bought-parts list that the kit is packed from.
- `kit`: what the kit adds to the hardware and firmware: the electronics as delivered, the enclosure, the packaging.
- `notes`: anything a buyer or a builder should know about this product version, such as enclosure or packaging changes.

## Making a product release

1. Set `version`, `date`, `hardware.tag`, `firmware.tag` and the manual, and describe kit changes in `kit` and `notes`.
2. Add a section `## [product-vX.Y.Z] - YYYY-MM-DD` to [CHANGELOG.md](../CHANGELOG.md).
3. Push to `main`. [`tools/release.py`](../tools/release.py) checks that both pinned tags exist and that the hardware status is allowed, then tags the commit and publishes a release with this lock file, the bill of materials, the manual and the assets of the pinned hardware and firmware releases.

A change that only touches the kit (enclosure, packaging, manual) gets a new product version without a new hardware or firmware tag.
