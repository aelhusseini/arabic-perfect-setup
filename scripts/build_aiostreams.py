"""Build the Arabic edition of the numb3rs AIOStreams template.

Reads numb3rs' AIOStreams.json and layers the Arabic changes on top, so every
numb3rs setting not mentioned here stays exactly as upstream ships it.

Usage:
  python3 build_aiostreams.py <numb3rs AIOStreams.json> <output.json>
      [--source-url URL]   where the output will be hosted; turns on AIOStreams'
                           "Apply Update" notifications for this template
      [--previous PATH]    the currently published output; the version is only
                           bumped (date-based) when the content really changed
"""
import argparse
import copy
import datetime
import json
import sys

ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("out")
ap.add_argument("--source-url")
ap.add_argument("--previous")
args = ap.parse_args()
src_path, out_path = args.src, args.out

FILE_VERSION = "1.6.2"  # version used for the downloadable file (no --previous)
CHANGELOG = [
    {
        "version": "1.6.2",
        "date": "2026-11-22",
        "content": (
            "- The third Aradeb link (Premiumize) is back: three links, one per debrid service, as in 1.6.0\n"
            "- A release found through more than one link still shows once (cached copy first, then "
            "service order)"
        ),
    },
    {
        "version": "1.6.1",
        "date": "2026-11-22",
        "content": (
            "- Two Aradeb links instead of three: TorBox (main) and AllDebrid (second). The third "
            "link field is gone; Premiumize still serves every other source"
        ),
    },
    {
        "version": "1.6.0",
        "date": "2026-11-22",
        "content": (
            "- Aradeb 2.0: each Aradeb configuration now has one debrid service and a UUID link; the "
            "three link fields say which configuration goes where\n"
            "- Aradeb Resources now brings Aradeb's Arabic search only, once its rows are turned off "
            "in Aradeb (they live in Xperience and Ali's collection pack instead)\n"
            "- Disney Arabic Dub: streams only, its row is no longer suggested (Aradeb's dubbed rows cover it)"
        ),
    },
    {
        "version": "1.5.0",
        "date": "2026-11-08",
        "content": (
            "- Removed TorBox Search: TorBox shut its search API down and AIOStreams disabled the addon\n"
            "- Added Usenet through TorBox Pro with your own Newznab indexer (up to two)\n"
            "- Usenet results are left out of the relaxed checks for Arabic originals"
        ),
    },
    {
        "version": "1.4.0",
        "date": "2026-11-08",
        "content": (
            "- Up to three Aradeb links (one per debrid service); extra links are streams only\n"
            "- Aradeb results still skip every filter but are now deduplicated, so a release found "
            "through two links shows once (cached copy first, then service order)"
        ),
    },
    {
        "version": "1.3.0",
        "date": "2026-11-08",
        "content": (
            "- Added optional TorBox Search addon with Usenet results (TorBox Pro)\n"
            "- Removed emojis from the Arabic layer's names, labels and expression names"
        ),
    },
    {
        "version": "1.2.0",
        "date": "2026-11-08",
        "content": "- Formatter Style now defaults to numb3rs' Flat Monochrome Icons",
    },
    {
        "version": "1.1.0",
        "date": "2026-11-08",
        "content": (
            "- Added Disney Arabic Dub addon (streams only by default, movies only, result passthrough)\n"
            "- Build supports hosting with automatic update notifications"
        ),
    },
    {
        "version": "1.0.0",
        "date": "2026-11-08",
        "content": (
            "- Forked from the numb3rs AIOStreams template\n"
            "- Added Aradeb custom addon (result passthrough, optional pin, own timeout)\n"
            "- Added Arabic-originals included expression (skips title/year/digital-release checks)\n"
            "- Added Arabic dub / hardsub ranked and excluded expressions\n"
            "- Added SubDL and SubSource subtitle addons\n"
            "- Defaults: languages Arabic + English, subtitles ar + en\n"
            "- Service order TorBox, AllDebrid, Premiumize; uncached dedup single result"
        ),
    },
]

tpl = json.load(open(src_path, encoding="utf-8"))
base_version = tpl["metadata"]["version"]
meta = tpl["metadata"]
cfg = tpl["config"]

# ---------------------------------------------------------------- metadata
meta["id"] = "arabic-edition.perfect-setup"
meta["name"] = "Streaming Perfect Setup · Arabic Edition"
meta["description"] = (
    "Arabic edition of the numb3rs Streaming Perfect Setup template "
    f"(based on v{base_version}, by Lucky Numb3rs, with TamTaro's SEL and Vidhin's regexes). "
    "Everything upstream is kept, plus an Arabic layer:\n"
    "* **Aradeb** (Arabic private trackers, up to one link per debrid service, duplicates merged) and **Disney Arabic Dub** in the same sorted list, never filtered out\n"
    "* Relaxed title/year/digital-release checks for **Arabic-original** titles only\n"
    "* Optional ranking for **Arabic dubs** and **Arabic hardsubs** on foreign titles\n"
    "* **SubDL / SubSource** Arabic subtitle addons\n"
    "* Optional **Usenet** from your own indexers, played through TorBox Pro\n"
    "* Debrid order TorBox → AllDebrid → Premiumize for duplicate cached results"
)
meta["source"] = "custom"
meta["author"] = "Numb3rs AR Edition"
meta["version"] = FILE_VERSION
meta.pop("sourceUrl", None)
meta.pop("changelogUrl", None)
if args.source_url:
    meta["source"] = "external"
    meta["sourceUrl"] = args.source_url
meta["changelog"] = copy.deepcopy(CHANGELOG)

inputs = meta["inputs"]


def find_input(input_id):
    for i, item in enumerate(inputs):
        if item.get("id") == input_id:
            return i, item
    raise KeyError(input_id)


# Formatter: numb3rs' Flat Monochrome Icons (the "flat" case of its formatter switch).
_, formatter_choice = find_input("formatterChoice")
assert any(o["value"] == "flat" for o in formatter_choice["options"]), "flat formatter missing upstream"
assert "flat" in cfg["formatter"]["cases"], "flat formatter case missing upstream"
formatter_choice["default"] = "flat"

# Language defaults: Arabic first, then English.
_, languages = find_input("languages")
assert any(o["value"] == "Arabic" for o in languages["options"]), "Arabic missing upstream"
languages["default"] = ["Arabic", "English"]
languages["description"] += (
    " *Arabic edition: Arabic and English are preselected. Arabic first means an Arabic-audio "
    "release wins a tie against an otherwise identical English one.*"
)

_, subtitles = find_input("subtitles")
assert any(o["value"] == "ar" for o in subtitles["options"]), "ar missing upstream"
subtitles["default"] = ["ar", "en"]

# Subtitle addon toggles go right after the Preferred Subtitles input.
sub_idx, _ = find_input("subtitles")
subtitle_inputs = [
    {
        "id": "subdl",
        "name": "SubDL Subtitles",
        "description": (
            "Adds the **SubDL** subtitles addon (Arabic + English), one of the largest Arabic "
            "subtitle libraries. Needs a free API key from "
            "[subdl.com/panel/api](https://subdl.com/panel/api). Edit its languages later in "
            "**Addons → SubDL**."
        ),
        "type": "boolean",
        "required": False,
        "default": False,
    },
    {
        "__if": "inputs.subdl",
        "id": "subdlApiKey",
        "name": "SubDL API Key",
        "description": "Your SubDL API key from [subdl.com/panel/api](https://subdl.com/panel/api).",
        "type": "password",
        "required": True,
    },
    {
        "id": "subsource",
        "name": "SubSource Subtitles",
        "description": (
            "Adds the **SubSource** subtitles addon (Arabic + English), another large Arabic "
            "subtitle library. Needs a free API key from your "
            "[SubSource profile](https://subsource.net/dashboard/profile)."
        ),
        "type": "boolean",
        "required": False,
        "default": False,
    },
    {
        "__if": "inputs.subsource",
        "id": "subsourceApiKey",
        "name": "SubSource API Key",
        "description": "Your SubSource API key from [subsource.net/dashboard/profile](https://subsource.net/dashboard/profile).",
        "type": "password",
        "required": True,
    },
]
inputs[sub_idx + 1:sub_idx + 1] = subtitle_inputs

# Arabic section goes right before the upstream Addon Options header.
addons_idx, _ = find_input("header.addons")
arabic_inputs = [
    {"id": "header.arabic", "name": "Arabic Options", "description": "", "type": "alert", "intent": "info"},
    {
        "id": "arabicInfo",
        "name": "",
        "description": (
            "These options add the Arabic layer on top of the numb3rs setup. The defaults are the "
            "recommended setup; the companion guide explains each one."
        ),
        "type": "alert",
        "intent": "info-basic",
    },
    {
        "id": "aradeb",
        "name": "Aradeb (Arabic Private Trackers)",
        "description": (
            "Adds **Aradeb** inside AIOStreams so its Arabic results are merged, sorted and formatted "
            "with everything else. Aradeb plays through the debrid service set **in each Aradeb "
            "configuration** (Aradeb 2.0 allows one per configuration), not the services you pick here. Its results skip every filter in this "
            "template, because Arabic release names often fail the normal title and language checks; "
            "only duplicates of the same release are merged. Keep the addon name **Aradeb**: the "
            "filter bypass looks for that name."
        ),
        "type": "boolean",
        "required": False,
        "default": True,
    },
    {
        "__if": "inputs.aradeb",
        "id": "aradebUrl",
        "name": "Aradeb Manifest URL",
        "description": (
            "The **Full manifest URL** of your Aradeb configuration for TorBox (aradeb.518878.xyz → "
            "Install, ends in **/manifest.json**). Recommended Aradeb settings for this one: "
            "Enhanced metadata **off**, Search **on**, Catalogs **Clear all**, so AIOStreams brings "
            "Aradeb's Arabic search and nothing else besides streams. The link can play through your "
            "debrid account, so keep it private."
        ),
        "type": "url",
        "required": True,
    },
    {
        "__if": "inputs.aradeb",
        "id": "aradebUrl2",
        "name": "Second Aradeb Manifest URL (optional)",
        "description": (
            "Aradeb allows one debrid service per configuration, so make one configuration per "
            "service and paste the AllDebrid one here to check that service's cache too. Extra links "
            "are asked for streams only, whatever rows the configuration has. When AIOStreams sees the same release from two links it "
            "keeps one: a cached copy beats an uncached one, and when both are cached the copy "
            "from the service higher in **Services** wins."
        ),
        "type": "url",
        "required": False,
    },
    {
        "__if": "inputs.aradeb",
        "id": "aradebUrl3",
        "name": "Third Aradeb Manifest URL (optional)",
        "description": (
            "The Aradeb configuration for a third debrid service (for example Premiumize). Turn "
            "everything off in it except the debrid service: it is only asked for streams."
        ),
        "type": "url",
        "required": False,
    },
    {
        "__if": "inputs.aradeb",
        "id": "aradebMode",
        "name": "Aradeb Resources",
        "description": (
            "* **Streams + Aradeb search** (recommended): AIOStreams also serves whatever catalogs the "
            "main Aradeb configuration has on. With its rows cleared in Aradeb, that is just Aradeb's "
            "Arabic and Latin title search.\n"
            "* **Streams only**: AIOStreams only asks Aradeb for streams."
        ),
        "type": "select",
        "required": False,
        "default": "full",
        "options": [
            {"value": "full", "label": "Streams + Aradeb search"},
            {"value": "streams", "label": "Streams only"},
        ],
    },
    {
        "__if": "inputs.aradeb",
        "id": "aradebPosition",
        "name": "Aradeb Position",
        "description": (
            "* **Sorted with everything** (recommended): Aradeb results compete on resolution, "
            "quality and score like any other source.\n"
            "* **Pinned on top**: Aradeb results always come first. Aradeb also answers for many "
            "foreign titles (often Arabic-hardsubbed), so pinning pushes those above better "
            "international releases."
        ),
        "type": "select",
        "required": False,
        "default": "none",
        "options": [
            {"value": "none", "label": "Sorted with everything"},
            {"value": "top", "label": "Always pinned on top"},
        ],
    },
    {
        "__if": "inputs.aradeb",
        "id": "aradebTimeout",
        "name": "Aradeb Timeout",
        "description": (
            "Time in ms to wait for Aradeb, which searches private trackers and can be slower than "
            "the other scrapers. AIOStreams waits for the slowest addon, so a higher value can make "
            "every result list slower."
        ),
        "type": "number",
        "required": False,
        "default": 8000,
    },
    {
        "id": "disneyDub",
        "name": "Disney Arabic Dub",
        "description": (
            "Adds the **Disney Arabic Dub** addon's streams (Arabic and Egyptian dubs of Disney films) "
            "for movies. Like Aradeb, its results skip every filter. It runs on a free server that "
            "sleeps when idle, so the first request after a quiet spell can time out; the next one works."
        ),
        "type": "boolean",
        "required": False,
        "default": True,
    },
    {
        "__if": "inputs.disneyDub",
        "id": "disneyDubUrl",
        "name": "Disney Arabic Dub Manifest URL",
        "description": "The addon's manifest link. The public one is pre-filled.",
        "type": "url",
        "required": True,
        "default": "https://disney-arabic-dub.onrender.com/manifest.json",
    },
    {
        "__if": "inputs.disneyDub",
        "id": "disneyDubCatalog",
        "name": "Disney Arabic Dub Catalog",
        "description": (
            "* **Streams only** (recommended): its Disney titles also appear in Aradeb's Arabic "
            "Dubbed Movies row, so no separate row is needed.\n"
            "* **Streams + catalog row**: AIOStreams also shows its *Disney (Arabic Dub)* row.\n"
            "Its metadata is never used: the addon claims metadata for every movie, which would "
            "override your metadata addon."
        ),
        "type": "select",
        "required": False,
        "default": "streams",
        "options": [
            {"value": "streams", "label": "Streams only"},
            {"value": "catalog", "label": "Streams + catalog row"},
        ],
    },
    {
        "id": "arabicOriginals",
        "name": "Relax Checks for Arabic Originals",
        "description": (
            "For titles whose original language is Arabic, results from ID-based scrapers skip the "
            "**title**, **year** and **digital release** checks. Arabic releases are named with "
            "transliterations (*El*, *Al*, *Wa*...) that rarely match TMDB exactly, and TMDB seldom "
            "lists digital release dates for Arab films, so these checks drop valid releases. All "
            "other filters still apply. Non-Arabic titles are unaffected."
        ),
        "type": "boolean",
        "required": False,
        "default": True,
    },
    {
        "id": "arabicDubs",
        "name": "Arabic-Dubbed Releases",
        "description": (
            "How to rank Arabic-dubbed releases of **non-Arabic** titles (detected from Arabic audio "
            "tags or words like *Arabic Dubbed* / *مدبلج*). Applies after resolution and quality.\n"
            "* **Neutral**: no change.\n"
            "* **Prefer**: dubbed releases move up within the same resolution and quality.\n"
            "* **Avoid**: dubbed releases move down, and are hidden when 10 or more better-scored "
            "results exist."
        ),
        "type": "select",
        "required": False,
        "default": "neutral",
        "options": [
            {"value": "neutral", "label": "Neutral"},
            {"value": "prefer", "label": "Prefer"},
            {"value": "avoid", "label": "Avoid"},
        ],
    },
    {
        "id": "arabicHardsubs",
        "name": "Arabic Hardsub Releases",
        "description": (
            "How to rank releases of **non-Arabic** titles with Arabic subtitles burned into the "
            "picture (words like *Arabic Sub* / *مترجم*). These are usually small re-encodes; with "
            "Arabic soft subtitles from OpenSubtitles, SubDL or SubSource you rarely need them.\n"
            "* **Neutral**: no change.\n"
            "* **Prefer**: move up within the same resolution and quality.\n"
            "* **Avoid**: move down, hidden when 10 or more better-scored results exist.\n"
            "* **Exclude**: always hidden (Aradeb results excepted)."
        ),
        "type": "select",
        "required": False,
        "default": "avoid",
        "options": [
            {"value": "neutral", "label": "Neutral"},
            {"value": "prefer", "label": "Prefer"},
            {"value": "avoid", "label": "Avoid"},
            {"value": "exclude", "label": "Exclude"},
        ],
    },
]
inputs[addons_idx:addons_idx] = arabic_inputs

# Usenet through TorBox Pro with your own Newznab indexer(s), the way numb3rs'
# guide does it (Additional Stuff -> Usenet). Goes into the upstream Addon
# Options section, just before the HTTP Addons choice. (TorBox Search, which
# used TorBox's own index, is gone: TorBox shut that API down and AIOStreams
# disabled the addon.)
NEWZNAB_INDEXERS = [  # from AIOStreams' Newznab preset; "Custom" is always possible
    ("abNZB", "https://abnzb.com/api"), ("altHUB", "https://api.althub.co.za/api"),
    ("AmeNZB", "https://amenzb.moe/api"), ("Anime Tosho", "https://feed.animetosho.net/api"),
    ("Aninzb", "https://aninzb.moe/api"), ("ClubNZB", "https://clubnzb.com/api"),
    ("Digital Carnage", "https://digitalcarnage.info/api"), ("DOGnzb", "https://api.dognzb.cr/api"),
    ("DrunkenSlug", "https://drunkenslug.com/api"), ("GingaDADDY", "https://www.gingadaddy.com/api"),
    ("Miatrix", "https://www.miatrix.com/api"), ("NewzBay", "https://newzbay.cc/api"),
    ("NinjaCentral", "https://ninjacentral.co.za/api"), ("NZB Atlas", "https://nzbatlas.com/api"),
    ("Nzb.life", "https://api.nzb.life/api"), ("NZBFinder", "https://nzbfinder.ws/api"),
    ("NZBgeek", "https://api.nzbgeek.info/api"), ("NzbNest", "https://nzbnest.com/api"),
    ("NzbNoob", "https://nzbnoob.com/api"), ("NzbPlanet", "https://api.nzbplanet.net/api"),
    ("NZBStars", "https://nzbstars.com/api"), ("PourCeSoir", "https://pourcesoir.in/api"),
    ("SearchNZB", "https://api.searchnzb.com/api"), ("SquareEyed", "https://squareeyed.org/api"),
    ("Tabula Rasa", "https://www.tabula-rasa.pw/api/v1/api"),
    ("Usenet Crawler", "https://www.usenet-crawler.com/api"), ("Videothek", "https://videothek.io/api"),
]


def nab_endpoint(input_id, name, description, required):
    return {
        "__if": "inputs.usenet",
        "id": input_id,
        "name": name,
        "description": description,
        "type": "nab-endpoint",
        "nab": {"namespace": "newznab", "preset": "newznab"},
        "required": required,
        "subOptions": [
            {
                "id": "url",
                "name": "Indexer",
                "description": "Pick your indexer, or choose Custom and paste its Newznab API URL (usually ending in /api).",
                "type": "select-with-custom",
                "required": required,
                "options": [{"label": l, "value": v} for l, v in NEWZNAB_INDEXERS],
            },
            {
                "id": "apiKey",
                "name": "API Key",
                "description": "The API key from your indexer profile page.",
                "type": "password",
                "required": False,
            },
        ],
    }


http_idx, _ = find_input("httpAddons")
inputs[http_idx:http_idx] = [
    {
        "__if": "services.torbox",
        "id": "usenet",
        "name": "Usenet through TorBox Pro",
        "description": (
            "Adds Usenet results from **your own indexer** (a paid NZB indexer account such as "
            "NZBgeek or NZBFinder), played through TorBox. Needs a TorBox **Pro** plan.\n"
            "* Results show as uncached; pressing play downloads the file to TorBox and starts "
            "it when ready, usually after a short wait.\n"
            "* Some indexers forbid this use, because the search comes from this AIOStreams "
            "server and the download from TorBox (two different IPs). Treasure Maps (formerly "
            "SceneNZBs) does; check your indexer's rules."
        ),
        "type": "boolean",
        "required": False,
        "default": False,
    },
    nab_endpoint("usenetIndexer", "Usenet Indexer", "Your Newznab indexer and its API key.", True),
    nab_endpoint(
        "usenetIndexer2", "Second Usenet Indexer (optional)",
        "Another indexer, if you have one. Leave the indexer empty to skip it.", False,
    ),
]

# Sorting info text: mention Aradeb.
_, sorting_info = find_input("sortingInfo")
sorting_info["description"] += (
    " \n *Arabic edition: Arabic dub/hardsub preferences act inside Stream Expression Score.*"
)

# Credits: keep upstream credits (they are the authors of nearly everything here).

# ---------------------------------------------------------------- config
cfg["services"] = [
    {"id": "torbox", "enabled": False, "credentials": {}},
    {"id": "alldebrid", "enabled": False, "credentials": {}},
    {"id": "premiumize", "enabled": False, "credentials": {}},
]

# With three debrid services, show one uncached copy (from the first service in
# the order above) instead of one per service.
cfg["deduplicator"]["uncached"] = "single_result"

presets = cfg["presets"]
lib_idx = next(i for i, p in enumerate(presets) if p.get("instanceId") == "lib")
aradeb_preset = {
    "__if": "inputs.aradeb",
    "category": "Arabic",
    "type": "custom",
    "instanceId": "ara",
    "enabled": True,
    "options": {
        "name": "Aradeb",
        "manifestUrl": "{{inputs.aradebUrl}}",
        "timeout": "{{inputs.aradebTimeout}}",
        "resources": {
            "__switch": "inputs.aradebMode",
            "cases": {"streams": ["stream"]},
            "default": ["stream", "catalog", "meta"],
        },
        "mediaTypes": [],
        "pinPosition": {
            "__switch": "inputs.aradebPosition",
            "cases": {"top": "top"},
            "default": {"__remove": True},
        },
        "libraryAddon": False,
        "formatPassthrough": False,
        # Not resultPassthrough: that would also skip deduplication. The
        # "Aradeb" included expression below bypasses every other stage.
        "resultPassthrough": False,
    },
}
# Extra Aradeb links (one per debrid service): streams only, same name so the
# included expression and the formatter treat them as one source.
aradeb_extra_presets = []
for n, iid in ((2, "ar2"), (3, "ar3")):
    extra = copy.deepcopy(aradeb_preset)
    extra["__if"] = f"inputs.aradeb and inputs.aradebUrl{n}"
    extra["instanceId"] = iid
    extra["options"]["manifestUrl"] = "{{inputs.aradebUrl%d}}" % n
    extra["options"]["resources"] = ["stream"]
    aradeb_extra_presets.append(extra)
disney_preset = {
    "__if": "inputs.disneyDub",
    "category": "Arabic",
    "type": "custom",
    "instanceId": "dad",
    "enabled": True,
    "options": {
        "name": "Disney Arabic Dub",
        "manifestUrl": "{{inputs.disneyDubUrl}}",
        "timeout": "{{inputs.timeout}}",
        # Never "meta": its manifest claims meta for every tt id.
        "resources": {
            "__switch": "inputs.disneyDubCatalog",
            "cases": {"catalog": ["stream", "catalog"]},
            "default": ["stream"],
        },
        "mediaTypes": ["movie"],
        "libraryAddon": False,
        "formatPassthrough": False,
        "resultPassthrough": True,
    },
}
presets[lib_idx + 1:lib_idx + 1] = [aradeb_preset, *aradeb_extra_presets, disney_preset]

# Usenet indexers (Newznab), played through TorBox only. Skipped for HTTP-only,
# like numb3rs' other debrid scrapers.
usenet_presets = []
for input_id, iid, name in (("usenetIndexer", "nzb", "Usenet"), ("usenetIndexer2", "nz2", "Usenet 2")):
    cond = "services.torbox and inputs.usenet and inputs.httpAddons != only"
    if input_id == "usenetIndexer2":
        cond += " and inputs.usenetIndexer2.url"
    usenet_presets.append({
        "__if": cond,
        "type": "newznab",
        "instanceId": iid,
        "enabled": True,
        "options": {
            "name": name,
            "api": {
                "url": "{{inputs.%s.url}}" % input_id,
                "apiKey": "{{inputs.%s.apiKey}}" % input_id,
            },
            "timeout": "{{inputs.timeout}}",
            "mediaTypes": [],
            "services": ["torbox"],
        },
    })
osb_pos = next(i for i, p in enumerate(presets) if p.get("instanceId") == "osb")
presets[osb_pos:osb_pos] = usenet_presets

subdl_preset = {
    "__if": "inputs.subdl",
    "type": "subdl",
    "instanceId": "sdl",
    "enabled": True,
    "options": {
        "name": "SubDL",
        "timeout": 15000,
        "resources": ["subtitles"],
        "subDlApiKey": "{{inputs.subdlApiKey}}",
        "language": ["AR", "EN"],
        "hearingImpairment": "hiInclude",
    },
}
subsource_preset = {
    "__if": "inputs.subsource",
    "type": "subsource",
    "instanceId": "sbs",
    "enabled": True,
    "options": {
        "name": "SubSource",
        "timeout": 15000,
        "resources": ["subtitles"],
        "subSourceApiKey": "{{inputs.subsourceApiKey}}",
        "language": ["Arabic", "English"],
        "subtitleTypes": [1, 2, 3, 4],
        "hearingImpairment": "hiInclude",
    },
}
osb_idx = next(i for i, p in enumerate(presets) if p.get("instanceId") == "osb")
presets[osb_idx + 1:osb_idx + 1] = [subdl_preset, subsource_preset]

cfg.setdefault("addonCategoryColors", {})["Arabic"] = "teal"

# ---------------------------------------------------------------- stream expressions
NON_ARABIC = "originalLanguage != 'Arabic'"
DUB_WORDS = [
    "arabic dub", "arabic dubbed", "arabic dubbing", "ar dub", "dub arabic", "dubbed arabic",
    "مدبلج", "مدبلجة", "دبلجة", "دوبلاج",
]
HARDSUB_WORDS = [
    "arabic sub", "arabic subs", "arabic subbed", "arabic subtitle", "arabic subtitles",
    "arabic hardsub", "arabic hardsubs", "ar sub", "ar subs", "arsub", "arsubs", "hardsub arabic",
    "مترجم", "مترجمة", "ترجمة",
]


def kw(words):
    return ", ".join("'" + w + "'" for w in words)


# Arabic-only audio (no English/original/dual/multi track alongside it), or
# explicitly labelled as an Arabic dub.
dub_select = (
    "merge(negate(language(streams, 'English', 'Original', 'Dual Audio', 'Multi'), "
    "language(streams, 'Arabic')), "
    f"keyword(streams, 'filename,folderName', {kw(DUB_WORDS)}))"
)
hardsub_select = f"keyword(streams, 'filename,folderName', {kw(HARDSUB_WORDS)})"

ranked = cfg.setdefault("rankedStreamExpressions", [])
ranked.extend([
    {
        "__if": "inputs.arabicDubs == prefer",
        "expression": f"/*AR Dub*/ {NON_ARABIC} ? {dub_select} : []",
        "score": 2000,
        "enabled": True,
    },
    {
        "__if": "inputs.arabicDubs == avoid",
        "expression": f"/*AR Dub*/ {NON_ARABIC} ? {dub_select} : []",
        "score": -2000,
        "enabled": True,
    },
    {
        "__if": "inputs.arabicHardsubs == prefer",
        "expression": f"/*AR Hardsub*/ {NON_ARABIC} ? {hardsub_select} : []",
        "score": 2000,
        "enabled": True,
    },
    {
        "__if": "inputs.arabicHardsubs == avoid",
        "expression": f"/*AR Hardsub*/ {NON_ARABIC} ? {hardsub_select} : []",
        "score": -2000,
        "enabled": True,
    },
])

excluded = cfg.setdefault("excludedStreamExpressions", [])
excluded.append({
    "__if": "inputs.arabicHardsubs == exclude",
    "expression": f"/*AR Hardsub Exclude*/ {NON_ARABIC} ? {hardsub_select} : []",
    "enabled": True,
})

included = cfg.setdefault("includedStreamExpressions", [])
included.append({
    "__if": "inputs.arabicOriginals",
    "expression": (
        "/*Arabic Originals*/ originalLanguage == 'Arabic' ? "
        "passthrough(negate(addon(streams, 'Knaben', 'Usenet', 'Usenet 2'), streams), 'title', 'year', 'digitalRelease') : []"
    ),
    "enabled": True,
})

# Aradeb: skip every filtering stage except deduplication, so the same release
# from two Aradeb links (or from Aradeb and a public scraper) is shown once.
ARADEB_STAGES = ["filter", "language", "subtitle", "limit", "excluded", "required",
                 "title", "year", "episode", "digitalRelease"]
included.append({
    "__if": "inputs.aradeb",
    "expression": "/*Aradeb*/ passthrough(addon(streams, 'Aradeb'), "
                  + ", ".join(f"'{s}'" for s in ARADEB_STAGES) + ")",
    "enabled": True,
})

# ---------------------------------------------------------------- versioning
# Hosted mode: keep the published version unless the content changed, then
# bump to a date-based version so AIOStreams offers "Apply Update".
def comparable(t):
    t = copy.deepcopy(t)
    for k in ("version", "changelog"):
        t["metadata"].pop(k, None)
    return json.dumps(t, sort_keys=True, ensure_ascii=False)


changed = True
if args.previous:
    try:
        prev = json.load(open(args.previous, encoding="utf-8"))
    except FileNotFoundError:
        prev = None
    if prev and comparable(prev) == comparable(tpl):
        changed = False
        meta["version"] = prev["metadata"]["version"]
        meta["changelog"] = prev["metadata"].get("changelog", meta["changelog"])
    else:
        now = datetime.datetime.now(datetime.timezone.utc)
        meta["version"] = f"{now.year}.{now.month * 100 + now.day}.{now.hour * 100 + now.minute}"
        older = prev["metadata"].get("changelog", []) if prev else meta["changelog"]
        meta["changelog"] = ([{
            "version": meta["version"],
            "date": now.strftime("%Y-%m-%d"),
            "content": f"- Rebuilt: numb3rs template (v{base_version}) or the Arabic layer changed",
        }] + older)[:20]

json.dump(tpl, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
open(out_path, "a", encoding="utf-8").write("\n")
print("wrote", out_path, "version:", meta["version"], "changed:", changed,
      "inputs:", len(inputs), "presets:", len(presets))
