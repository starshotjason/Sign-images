# StreetZim sign-reader photo set (world)

**1949 openly licensed photos of street signs, address plates, business signs and landmark name boards across 191 countries**, 1944 of them visually transcribed (1782 MB). Built for the photo search (`--ocr` sign reader) in [jasontitus/streetzim](https://github.com/jasontitus/streetzim), using the record format of its `docs/ocr-test-set.md` and `tests/fixtures/ocr-signs/`.

Score it with streetzim's runner:

```sh
python3 tools/ocr_photos.py --set <this repo>/ocr-signs --maps <maps folder> --out <out>
```

## Layout

- `ocr-signs/manifest.jsonl`: every record. `ocr-signs/<cc>/`: photos, `.source.json` provenance sidecars and the country's `manifest.jsonl`.
- `ocr-signs/ATTRIBUTIONS.md`: per-photo credits. **Each photo keeps its own licence** (CC0 / PD / CC BY / CC BY-SA / OGDL-Taiwan); this repo's code licence does not apply to them.
- `labels/`: raw review decisions, including rejects with reasons. `scripts/`: the crawl/rank/fetch/assemble pipeline. `LABELING.md`: the transcription rules.

## Status of labels

- `label_status: visually transcribed`: `lines`, `kind`, `scripts`, `expect.query/type`, `difficulty` written by a reviewer looking at the photo.
- `label_status: unlabelled ...`: licence and provenance are complete, but `kind`/`scripts` are guessed from source categories and `lines` is empty.
- **No `expect.record`/`expect.near` is map-verified yet** (`map_verification: pending`). `location` is the camera position when the source published one, never the target.

## Image provenance

This cloud crawler's IP was throttled by Wikimedia's and Flickr's original-file servers, so some files are the sources' own published renditions rather than originals; each record's `derivative` field says exactly which (empty = byte-unmodified original):

- 1459: original
- 28: Flickr's published 1024 px 'large' rendition, served by the Openverse image API
- 22: whole 4000x3000 HD picture as served by the Panoramax instance
- 16: rectilinear
- 10: whole 1280x960 HD picture as served by the Panoramax instance
- 10: whole 4032x3024 HD picture as served by the Panoramax instance
- 8: whole 3840x2160 full-size processed
- 7: crop 720,0,1920,900 of the 1920x1080 full-size processed
- 6: whole 3072x1728 full-size processed
- 6: whole 3264x2448 full-size processed
- 5: whole 3264x1836 full-size processed
- 5: whole 3072x4080 HD picture as served by the Panoramax instance
- 5: whole 1920x1080 full-size processed
- 4: whole 4080x3060 HD picture as served by the Panoramax instance
- 4: crop 0,0,1200,900 of the 1920x1080 full-size processed
- 4: whole 4096x2304 full-size processed
- 4: whole 3840x2160 HD picture as served by the Panoramax instance
- 4: whole 1440x1080 HD picture as served by the Panoramax instance
- 3: Wikimedia Commons standard 1920px-wide rendition
- 3: whole 3072x1728 HD picture as served by the Panoramax instance
- 3: whole 4000x2250 HD picture as served by the Panoramax instance
- 3: whole 3072x4096 HD picture as served by the Panoramax instance
- 3: crop 0,0,1200,900 of the 1440x1080 full-size processed
- 3: whole 4032x3024 full-size processed
- 3: whole 3264x2448 HD picture as served by the Panoramax instance
- 3: whole 4624x2604 HD picture as served by the Panoramax instance
- 3: whole 4080x2295 HD picture as served by the Panoramax instance
- 2: whole 1049x634 HD picture as served by the Panoramax instance
- 2: whole 3264x1840 full-size processed
- 2: whole 4128x2322 full-size processed
- 2: whole 4160x2340 HD picture as served by the Panoramax instance
- 2: whole 2160x3840 HD picture as served by the Panoramax instance
- 2: whole 2880x1620 full-size processed
- 2: whole 4000x3000 full-size processed
- 2: whole 2592x1936 full-size processed
- 2: whole 1440x1920 HD picture as served by the Panoramax instance
- 2: whole 1816x4032 HD picture as served by the Panoramax instance
- 2: whole 4344x5792 HD picture as served by the Panoramax instance
- 2: whole 4000x2250 full-size processed
- 1: crop 1887,0,4623,2052 of the 4624x3468 HD picture
- 1: crop 803,912,2175,1941 of the 4624x3468 HD picture
- 1: crop 75,0,3405,2160 of the 3840x2160 HD picture
- 1: crop 80,0,1280,720 of the 1280x720 full-size processed
- 1: crop 0,0,2244,1683 of the 3072x1728 full-size processed
- 1: crop 315,12,1677,1033 of the 3072x1728 full-size processed
- 1: crop 0,224,1200,1124 of the 3072x1728 full-size processed
- 1: crop 736,788,1936,1688 of the 1936x2592 full-size processed
- 1: crop 0,0,3450,2160 of the 3840x2160 full-size processed
- 1: crop 0,0,1200,900 of the 3840x2160 full-size processed
- 1: crop 0,1279,1200,2179 of the 3000x4000 HD picture
- 1: whole 1051x634 HD picture as served by the Panoramax instance
- 1: crop 2224,699,3424,1599 of the 4128x2322 full-size processed
- 1: crop 2928,484,4128,1384 of the 4128x2322 full-size processed
- 1: crop 2928,526,4128,1426 of the 4128x2322 full-size processed
- 1: crop 2832,0,4032,900 of the 4032x3024 HD picture
- 1: crop 1117,1087,2317,1987 of the 4000x3000 full-size processed
- 1: crop 1164,790,3180,2302 of the 4080x3060 HD picture
- 1: crop 770,487,2220,1574 of the 4080x3060 HD picture
- 1: crop 733,0,4079,2510 of the 4080x3060 HD picture
- 1: whole 1884x4080 HD picture as served by the Panoramax instance
- 1: crop 1126,0,4031,2179 of the 4032x3024 HD picture
- 1: whole 1050x634 HD picture as served by the Panoramax instance
- 1: crop 1012,326,2610,1524 of the 4032x3024 HD picture
- 1: whole 4160x3120 full-size processed
- 1: crop 1614,1210,4031,3023 of the 4032x3024 HD picture
- 1: crop 1083,1652,2437,2668 of the 4080x3060 HD picture
- 1: crop 0,0,3060,3433 of the 3060x4080 HD picture
- 1: crop 0,866,3060,3651 of the 3060x4080 HD picture
- 1: crop 1629,868,3621,2362 of the 4080x3060 HD picture
- 1: whole 5152x2898 HD picture as served by the Panoramax instance
- 1: crop 278,226,1478,1126 of the 2592x1936 full-size processed
- 1: crop 2800,47,4000,947 of the 4000x3000 full-size processed
- 1: crop 1318,647,2644,1641 of the 3264x2448 full-size processed
- 1: crop 659,0,1859,900 of the 1920x1080 full-size processed
- 1: crop 540,0,1740,900 of the 1920x1080 full-size processed
- 1: crop 713,0,1913,900 of the 1920x1080 full-size processed
- 1: crop 0,0,2665,1999 of the 3060x4080 HD picture
- 1: crop 1203,0,4079,2157 of the 4080x3060 HD picture
- 1: crop 0,560,1562,1731 of the 4000x2250 full-size processed
- 1: crop 2020,275,3220,1175 of the 3264x1836 full-size processed
- 1: crop 1711,1005,4031,2745 of the 4032x3024 full-size processed
- 1: crop 532,284,1732,1184 of the 3264x1836 full-size processed
- 1: crop 2064,0,3264,900 of the 3264x1836 full-size processed
- 1: crop 0,0,2828,2121 of the 4000x2250 full-size processed
- 1: crop 448,0,3072,1728 of the 3072x1728 HD picture
- 1: whole 3264x1504 HD picture as served by the Panoramax instance
- 1: crop 0,705,1728,3071 of the 1728x3072 HD picture
- 1: crop 914,1409,2114,2309 of the 3024x4032 HD picture
- 1: crop 1046,0,3981,2201 of the 4160x3120 full-size processed
- 1: crop 544,757,1744,1657 of the 2592x1936 full-size processed
- 1: crop 1017,456,2591,1636 of the 2592x1936 full-size processed
- 1: crop 0,0,2601,1836 of the 3264x1836 full-size processed
- 1: whole 2688x1520 full-size processed
- 1: crop 0,219,2550,2131 of the 3840x2160 full-size processed
- 1: crop 0,211,2813,2321 of the 4128x2322 full-size processed
- 1: crop 1192,0,3263,1553 of the 3264x1836 full-size processed
- 1: crop 0,0,2456,1836 of the 3264x1836 full-size processed
- 1: crop 1463,0,2688,918 of the 2688x1520 full-size processed
- 1: crop 802,0,3839,2160 of the 3840x2160 full-size processed
- 1: crop 0,255,2691,2273 of the 4608x2592 full-size processed
- 1: crop 0,367,1200,1267 of the 3840x2160 full-size processed
- 1: crop 1013,0,3117,1578 of the 4096x2304 full-size processed
- 1: crop 1990,75,3190,975 of the 3264x1836 full-size processed
- 1: crop 131,0,4045,2304 of the 4096x2304 full-size processed
- 1: crop 0,445,1576,1627 of the 4096x2304 full-size processed
- 1: crop 1184,0,3389,1653 of the 4608x2592 full-size processed
- 1: crop 0,0,1800,1350 of the 2560x1440 full-size processed
- 1: whole 3280x2464 HD picture as served by the Panoramax instance
- 1: whole 4096x3072 HD picture as served by the Panoramax instance
- 1: crop 0,0,1717,1080 of the 1920x1080 full-size processed
- 1: crop 1255,0,3263,1506 of the 3264x1836 full-size processed
- 1: crop 720,150,1920,1050 of the 1920x1080 full-size processed
- 1: crop 473,388,1730,1331 of the 4000x2250 full-size processed
- 1: crop 931,318,2131,1218 of the 4000x2250 full-size processed
- 1: crop 0,187,1200,1087 of the 2560x1440 full-size processed
- 1: crop 268,0,1920,1080 of the 1920x1080 full-size processed
- 1: crop 0,0,2080,1440 of the 2560x1440 full-size processed
- 1: whole 2117x2822 HD picture as served by the Panoramax instance
- 1: whole 2340x4160 HD picture as served by the Panoramax instance
- 1: crop 0,384,2160,2184 of the 2160x3840 HD picture
- 1: crop 0,464,1200,1364 of the 3840x2160 HD picture
- 1: whole 4284x5712 HD picture as served by the Panoramax instance
- 1: whole 2688x1512 full-size processed
- 1: crop 1413,866,3541,2462 of the 4160x3120 HD picture
- 1: crop 1065,342,2265,1242 of the 4160x3120 HD picture
- 1: crop 0,62,1984,1550 of the 4080x3060 HD picture
- 1: crop 0,600,3134,2950 of the 4080x3060 HD picture
- 1: crop 0,1275,2178,2908 of the 4080x3060 HD picture
- 1: crop 2559,0,4031,1104 of the 4032x2268 HD picture
- 1: whole 3264x1836 HD picture as served by the Panoramax instance
- 1: crop 0,882,2375,2663 of the 4000x3000 HD picture
- 1: crop 1636,0,4905,2452 of the 6000x4000 HD picture
- 1: crop 240,149,1440,1049 of the 1440x1080 full-size processed
- 1: crop 466,23,1666,923 of the 1920x1080 full-size processed
- 1: crop 0,750,3000,3000 of the 4000x3000 HD picture
- 1: crop 594,225,1874,1185 of the 3072x1728 full-size processed
- 1: crop 0,0,2512,1728 of the 3072x1728 full-size processed
- 1: crop 0,0,1784,1080 of the 1920x1080 full-size processed
- 1: crop 0,648,2820,2763 of the 4000x3000 full-size processed
- 1: crop 2800,1088,4000,1988 of the 4000x3000 HD picture
- 1: crop 395,0,3999,2703 of the 4000x3000 HD picture
- 1: crop 1270,0,2470,900 of the 4000x3000 HD picture
- 1: crop 460,53,3999,2707 of the 4000x3000 full-size processed
- 1: crop 2023,307,4031,1813 of the 4032x1814 HD picture
- 1: crop 1623,0,3210,1190 of the 3264x1836 full-size processed
- 1: crop 1804,122,3004,1022 of the 3264x1836 full-size processed
- 1: crop 1934,83,3217,1045 of the 4032x1814 HD picture
- 1: crop 2832,672,4032,1572 of the 4032x1814 HD picture
- 1: crop 1415,125,3072,1368 of the 3264x1836 full-size processed
- 1: crop 2064,99,3264,999 of the 3264x1836 full-size processed
- 1: whole 3264x1448 HD picture as served by the Panoramax instance
- 1: crop 1421,129,3263,1510 of the 3264x1836 full-size processed
- 1: crop 0,298,2065,1847 of the 2592x1944 full-size processed
- 1: crop 0,923,1200,1823 of the 2592x1944 full-size processed
- 1: crop 0,0,3060,3115 of the 3060x4080 HD picture
- 1: crop 1181,1245,2511,2242 of the 5120x3840 full-size processed
- 1: crop 2844,758,4279,1834 of the 12048x3584 HD picture
- 1: crop 1319,539,2563,1472 of the 4032x3024 full-size processed
- 1: crop 1134,852,2334,1752 of the 4032x3024 full-size processed
- 1: crop 2350,499,3736,1538 of the 4032x3024 full-size processed
- 1: crop 1623,297,3263,1527 of the 3264x2448 HD picture
- 1: crop 0,0,2435,1826 of the 3264x2448 HD picture
- 1: crop 0,0,2830,2122 of the 3264x2448 HD picture
- 1: whole 1080x1920 HD picture as served by the Panoramax instance
- 1: crop 810,1836,4115,4314 of the 4284x5712 HD picture
- 1: crop 0,766,4284,5711 of the 4284x5712 HD picture
- 1: crop 0,0,3024,3537 of the 3024x4032 HD picture
- 1: crop 0,1528,4284,5456 of the 4284x5712 HD picture
- 1: whole 5712x4284 HD picture as served by the Panoramax instance
- 1: whole 1077x1080 HD picture as served by the Panoramax instance
- 1: crop 100,0,1300,900 of the 1440x1080 HD picture
- 1: crop 0,559,1974,2039 of the 4032x2268 HD picture
- 1: whole 4032x2268 HD picture as served by the Panoramax instance
- 1: crop 0,0,3108,2268 of the 4032x2268 HD picture
- 1: crop 1081,8,4031,2220 of the 4032x2268 HD picture
- 1: crop 0,0,1445,1083 of the 4000x3000 HD picture
- 1: crop 0,186,1080,1086 of the 1080x1920 HD picture
- 1: whole 2100x2800 HD picture as served by the Panoramax instance
- 1: crop 40,0,1920,1080 of the 1920x1080 HD picture
- 1: crop 1934,274,3952,1788 of the 4080x3060 HD picture
- 1: whole 5568x4872 HD picture as served by the Panoramax instance
- 1: whole 4608x3456 full-size processed
- 1: crop 1633,130,3613,1615 of the 3840x2160 full-size processed
- 1: whole 2688x1512 HD picture as served by the Panoramax instance
- 1: crop 0,617,1200,1517 of the 3264x2448 full-size processed
- 1: whole 3024x4032 HD picture as served by the Panoramax instance
- 1: crop 690,265,1890,1165 of the 2160x2160 full-size processed
- 1: crop 1503,0,2996,1120 of the 3096x4128 HD picture
- 1: crop 146,222,2331,1860 of the 3024x4032 HD picture
- 1: crop 240,1020,1440,1920 of the 1440x1920 HD picture
- 1: crop 558,0,4608,1589 of the 4608x1589 full-size processed
- 1: crop 1393,235,4550,2602 of the 5712x4284 HD picture
- 1: whole 8064x6048 HD picture as served by the Panoramax instance
- 1: crop 0,334,2232,2008 of the 4608x2592 HD picture
- 1: crop 625,0,3641,2262 of the 4624x2604 HD picture
- 1: crop 0,448,1816,2118 of the 1816x4032 HD picture
- 1: crop 0,1044,1252,1983 of the 1816x4032 HD picture
- 1: crop 0,1418,1200,2318 of the 2268x4032 HD picture
- 1: crop 140,1596,1789,2832 of the 1816x4032 HD picture
- 1: crop 121,1703,1321,2603 of the 1816x4032 HD picture
- 1: crop 819,1574,3379,3494 of the 4284x5712 HD picture
- 1: whole 3014x3997 HD picture as served by the Panoramax instance
- 1: crop 1283,904,2483,1804 of the 3840x2160 full-size processed
- 1: whole 3500x2636 HD picture as served by the Panoramax instance
- 1: crop 2375,1,3737,1022 of the 4032x3024 full-size processed
- 1: whole 4080x3072 HD picture as served by the Panoramax instance
- 1: crop 1995,57,3840,1440 of the 3840x2160 HD picture
- 1: crop 2279,163,4079,1513 of the 4080x3072 HD picture
- 1: crop 1392,570,2592,1470 of the 2592x1936 full-size processed
- 1: crop 0,639,1200,1539 of the 2592x1936 full-size processed
- 1: crop 1907,937,3118,1845 of the 3264x2448 full-size processed
- 1: crop 0,615,3072,4053 of the 3072x4080 HD picture
- 1: crop 605,193,1805,1093 of the 2592x1936 full-size processed
- 1: crop 0,201,1814,1734 of the 1814x2419 HD picture
- 1: crop 2609,1023,3999,2065 of the 4000x3000 full-size processed
- 1: crop 2620,1265,3820,2165 of the 4000x3000 full-size processed
- 1: crop 0,0,2192,1512 of the 2592x1512 full-size processed
- 1: crop 1080,194,2592,1328 of the 2592x1512 full-size processed
- 1: crop 0,391,1200,1291 of the 2592x1512 full-size processed
- 1: crop 0,384,1200,1284 of the 2592x1512 full-size processed
- 1: crop 602,356,1802,1256 of the 2688x1520 full-size processed
- 1: crop 1872,309,3072,1209 of the 3072x1728 full-size processed
- 1: crop 2356,557,3556,1457 of the 3840x2160 HD picture
- 1: whole 4096x2160 HD picture as served by the Panoramax instance
- 1: crop 2800,214,4000,1114 of the 4000x2250 full-size processed
- 1: crop 360,342,2029,1594 of the 4032x3024 HD picture
- 1: crop 817,306,2017,1206 of the 4032x3024 HD picture
- 1: crop 0,559,2793,2653 of the 4032x3024 HD picture
- 1: crop 0,2388,4344,5747 of the 4344x5792 HD picture
- 1: crop 264,1404,3680,3966 of the 4344x5792 HD picture
- 1: crop 1649,266,3264,1477 of the 3264x1478 HD picture
- 1: crop 1269,413,2592,1405 of the 2592x1936 full-size processed
- 1: crop 425,0,4031,2705 of the 4032x3024 HD picture
- 1: crop 0,513,1200,1413 of the 2592x1936 full-size processed
- 1: crop 1436,0,2908,1104 of the 3264x1836 full-size processed
- 1: crop 6752,863,8908,2480 of the 13304x3632 HD picture
- 1: crop 1952,1123,3152,2023 of the 4032x3024 full-size processed
- 1: crop 705,0,2560,1391 of the 2560x1440 HD picture
- 1: crop 2610,597,3840,1519 of the 3840x2160 full-size processed
- 1: crop 1901,697,3354,1787 of the 13288x3352 HD picture
- 1: crop 2640,390,3840,1290 of the 3840x2160 full-size processed
- 1: crop 2584,792,3784,1692 of the 4000x2250 full-size processed
- 1: crop 0,246,1200,1146 of the 4032x3024 HD picture
- 1: crop 302,1063,1502,1963 of the 4032x3024 HD picture
- 1: crop 1680,0,2880,900 of the 2880x1728 full-size processed
- 1: crop 1648,274,2879,1197 of the 2880x1728 full-size processed
- 1: crop 2063,1001,4079,2513 of the 4080x3060 HD picture
- 1: crop 0,0,1200,1218 of the 1200x1600 HD picture
- 1: crop 218,646,1418,1546 of the 4032x3024 HD picture
- 1: crop 802,1089,2002,1989 of the 4032x3024 HD picture
- 1: crop 0,479,2845,2613 of the 4032x3024 HD picture
- 1: crop 0,624,3072,4080 of the 3072x4080 HD picture
- 1: whole 3953x2965 HD picture as served by the Panoramax instance
- 1: crop 1590,306,4031,2136 of the 4032x3024 full-size processed
- 1: crop 0,578,1200,1478 of the 3840x2160 full-size processed
- 1: crop 2135,854,3859,2147 of the 4032x3024 HD picture
- 1: whole 4208x3120 full-size processed
- 1: crop 248,471,3146,2644 of the 4032x3024 HD picture
- 1: crop 310,0,3840,2160 of the 3840x2160 HD picture
- 1: crop 0,120,2385,1908 of the 3840x2160 full-size processed
- 1: crop 250,359,3930,3119 of the 4160x3120 HD picture
- 1: crop 314,0,1514,900 of the 2592x1936 full-size processed
- 1: crop 311,37,1888,1219 of the 5312x2988 full-size processed
- 1: crop 3846,1071,5046,1971 of the 5184x3888 HD picture
- 1: crop 2625,110,4000,1141 of the 4000x3000 HD picture
- 1: crop 0,558,2625,2526 of the 4000x3000 HD picture
- 1: crop 1498,0,5183,2764 of the 5184x3888 HD picture
- 1: crop 573,0,2591,1513 of the 2592x1936 full-size processed
- 1: crop 462,231,1662,1131 of the 2000x1500 HD picture
- 1: whole 2448x3264 HD picture as served by the Panoramax instance
- 1: crop 167,10,4079,2944 of the 4080x3060 HD picture
- 1: crop 307,636,2960,2626 of the 4080x3060 HD picture
- 1: crop 975,1,3263,1717 of the 3264x2448 full-size processed
- 1: crop 0,0,2709,2031 of the 4032x3024 HD picture
- 1: crop 1872,378,3072,1278 of the 3072x1728 full-size processed
- 1: crop 1497,129,2835,1132 of the 3072x1728 full-size processed
- 1: crop 0,0,1755,1316 of the 2160x3840 full-size processed
- 1: crop 414,0,1614,900 of the 3072x1728 full-size processed
- 1: crop 1536,265,3911,2046 of the 4000x2250 full-size processed
- 1: crop 2054,460,3999,1918 of the 4000x2250 full-size processed
- 1: crop 0,0,1781,1335 of the 4000x2250 full-size processed
- 1: crop 757,0,3999,2250 of the 4000x2250 full-size processed
- 1: crop 1881,404,3081,1304 of the 4000x2250 full-size processed
- 1: crop 2500,30,4000,1155 of the 4000x2250 full-size processed
- 1: crop 2718,0,3978,945 of the 4000x2250 full-size processed
- 1: crop 2429,279,3999,1456 of the 4000x2250 full-size processed
- 1: crop 0,0,3000,3810 of the 3000x4000 HD picture
- 1: crop 555,327,2312,1645 of the 3000x4000 HD picture
- 1: whole 3000x4000 HD picture as served by the Panoramax instance
- 1: crop 0,0,3123,2342 of the 3264x2448 full-size processed
- 1: crop 1031,0,2999,1476 of the 3000x4000 HD picture
- 1: crop 892,0,3263,1778 of the 3264x2448 full-size processed
- 1: crop 0,675,2187,2315 of the 4000x3000 HD picture
- 1: crop 0,794,1742,2100 of the 4000x3000 HD picture
- 1: crop 0,163,1200,1063 of the 3072x1728 full-size processed
- 1: whole 2560x1920 full-size processed
- 1: crop 0,411,2160,2203 of the 2160x3840 HD picture
- 1: crop 560,420,3983,2987 of the 3984x2988 full-size processed
- 1: crop 70,0,3590,1844 of the 4096x1844 HD picture
- 1: whole 4096x1844 HD picture as served by the Panoramax instance
- 1: crop 240,0,4096,1844 of the 4096x1844 HD picture
- 1: crop 1808,0,3440,1224 of the 4096x1844 HD picture
- 1: crop 279,353,1609,1351 of the 4080x2295 HD picture
- 1: crop 550,0,3745,2295 of the 4080x2295 HD picture
- 1: crop 62,0,2253,1643 of the 4080x2295 HD picture
- 1: crop 1243,0,3263,1515 of the 3264x2448 full-size processed
- 1: crop 0,0,2263,1697 of the 4080x2295 HD picture
- 1: crop 0,0,2932,2199 of the 4080x2295 HD picture
- 1: crop 2386,443,3586,1343 of the 3840x2160 full-size processed
- 1: whole 3840x1830 full-size processed
- 1: crop 0,313,1657,1556 of the 3840x2160 full-size processed
- 1: crop 1163,347,3064,1772 of the 4160x3120 HD picture
- 1: crop 536,0,2591,1541 of the 2592x1936 full-size processed
- 1: crop 857,748,3002,2356 of the 4160x3120 HD picture
- 1: crop 0,484,1523,1626 of the 2592x1936 full-size processed
- 1: whole 4160x3120 HD picture as served by the Panoramax instance
- 1: crop 1680,0,3840,1620 of the 3840x2160 full-size processed
- 1: crop 428,0,1920,1080 of the 1920x1080 full-size processed
- 1: crop 720,180,1920,1080 of the 1920x1080 full-size processed
- 1: crop 0,131,1200,1031 of the 1920x1080 full-size processed
- 1: crop 425,155,1625,1055 of the 1920x1080 full-size processed
- 1: crop 0,80,1200,980 of the 1920x1080 full-size processed
- 1: crop 0,60,1815,1421 of the 3840x2160 full-size processed
- 1: crop 2227,303,3622,1349 of the 3840x2160 full-size processed
- 1: crop 1208,544,2408,1444 of the 3840x2160 full-size processed
- 1: crop 2285,497,3485,1397 of the 3840x2160 full-size processed
- 1: whole 4080x1836 HD picture as served by the Panoramax instance
- 1: crop 2342,0,3542,900 of the 4080x1836 HD picture
- 1: crop 718,283,1918,1183 of the 4080x1836 HD picture
- 1: crop 0,814,1362,1835 of the 4080x1836 HD picture

## Coverage

| Source | Photos |
|---|---:|
| commons | 1230 |
| panoramax | 250 |
| flickr | 233 |
| kartaview | 209 |
| tcmb | 14 |
| gongu | 13 |

| Kind | Photos |
|---|---:|
| business sign | 662 |
| landmark | 570 |
| street sign | 418 |
| hard | 136 |
| transit | 58 |
| address plate | 41 |
| building tag | 36 |
| negative | 24 |
| bilingual | 2 |
| road sign | 1 |
| sign | 1 |

| Licence | Photos |
|---|---:|
| CC BY-SA 4.0 | 1062 |
| CC BY 2.0 | 234 |
| CC BY-SA 3.0 | 210 |
| CC BY-SA 2.0 | 153 |
| CC0 1.0 | 107 |
| CC BY 3.0 | 71 |
| CC BY 4.0 | 62 |
| Public domain | 46 |
| CC BY 2.5 | 3 |
| OGDL-Taiwan-1.0 | 1 |

### By country

| Country | Script | Income | Photos | Transcribed | Target |
|---|---|---|---:|---:|---:|
| AF Afghanistan | Arabic | L | 8 | 8 | 15 |
| AL Albania | Latin | UM | 12 | 12 | 12 |
| DZ Algeria | Arabic | UM | 15 | 15 | 15 |
| AD Andorra | Latin | H | 10 | 10 | 10 |
| AO Angola | Latin | LM | 3 | 3 | 12 |
| AG Antigua and Barbuda | Latin | H | 5 | 4 | 10 |
| AR Argentina | Latin | UM | 12 | 12 | 12 |
| AM Armenia | Armenian | UM | 15 | 15 | 15 |
| AU Australia | Latin | H | 10 | 10 | 10 |
| AT Austria | Latin | H | 10 | 10 | 10 |
| AZ Azerbaijan | Latin | UM | 12 | 12 | 12 |
| BS Bahamas | Latin | H | 10 | 10 | 10 |
| BH Bahrain | Arabic | H | 8 | 8 | 15 |
| BD Bangladesh | Bengali | LM | 15 | 15 | 15 |
| BB Barbados | Latin | H | 10 | 10 | 10 |
| BY Belarus | Cyrillic | UM | 15 | 15 | 15 |
| BE Belgium | Latin | H | 10 | 10 | 10 |
| BZ Belize | Latin | UM | 12 | 12 | 12 |
| BJ Benin | Latin | LM | 12 | 12 | 12 |
| BT Bhutan | Tibetan | LM | 15 | 15 | 15 |
| BO Bolivia | Latin | LM | 12 | 12 | 12 |
| BA Bosnia and Herzegovina | Latin | UM | 12 | 12 | 12 |
| BW Botswana | Latin | UM | 10 | 10 | 12 |
| BR Brazil | Latin | UM | 12 | 12 | 12 |
| BN Brunei | Latin | H | 10 | 10 | 10 |
| BG Bulgaria | Cyrillic | H | 15 | 15 | 15 |
| BF Burkina Faso | Latin | L | 7 | 7 | 15 |
| BI Burundi | Latin | L | 15 | 15 | 15 |
| KH Cambodia | Khmer | LM | 15 | 15 | 15 |
| CM Cameroon | Latin | LM | 9 | 9 | 12 |
| CA Canada | Latin | H | 10 | 10 | 10 |
| CV Cape Verde | Latin | LM | 12 | 12 | 12 |
| CF Central African Republic | Latin | L | 4 | 4 | 15 |
| TD Chad | Arabic | L | 0 | 0 | 15 |
| CL Chile | Latin | H | 10 | 10 | 10 |
| CN China | Han | UM | 15 | 15 | 15 |
| CO Colombia | Latin | UM | 12 | 12 | 12 |
| KM Comoros | Latin | LM | 0 | 0 | 12 |
| CR Costa Rica | Latin | UM | 12 | 12 | 12 |
| HR Croatia | Latin | H | 10 | 10 | 10 |
| CU Cuba | Latin | UM | 12 | 12 | 12 |
| CY Cyprus | Greek | H | 15 | 15 | 15 |
| CZ Czech Republic | Latin | H | 10 | 10 | 10 |
| CD DR Congo | Latin | L | 0 | 0 | 15 |
| DK Denmark | Latin | H | 10 | 10 | 10 |
| DJ Djibouti | Arabic | LM | 1 | 1 | 15 |
| DM Dominica | Latin | UM | 3 | 3 | 12 |
| DO Dominican Republic | Latin | UM | 3 | 3 | 12 |
| EC Ecuador | Latin | UM | 12 | 12 | 12 |
| EG Egypt | Arabic | LM | 15 | 15 | 15 |
| SV El Salvador | Latin | UM | 6 | 6 | 12 |
| GQ Equatorial Guinea | Latin | UM | 0 | 0 | 12 |
| ER Eritrea | Ethiopic | L | 4 | 4 | 15 |
| EE Estonia | Latin | H | 10 | 10 | 10 |
| SZ Eswatini | Latin | LM | 4 | 4 | 12 |
| ET Ethiopia | Ethiopic | L | 15 | 15 | 15 |
| FJ Fiji | Latin | UM | 12 | 12 | 12 |
| FI Finland | Latin | H | 10 | 10 | 10 |
| FR France | Latin | H | 10 | 10 | 10 |
| GA Gabon | Latin | UM | 1 | 1 | 12 |
| GM Gambia | Latin | L | 6 | 6 | 15 |
| GE Georgia | Georgian | UM | 15 | 15 | 15 |
| DE Germany | Latin | H | 10 | 10 | 10 |
| GH Ghana | Latin | LM | 12 | 12 | 12 |
| GR Greece | Greek | H | 15 | 15 | 15 |
| GD Grenada | Latin | UM | 3 | 3 | 12 |
| GT Guatemala | Latin | UM | 12 | 12 | 12 |
| GN Guinea | Latin | LM | 1 | 1 | 12 |
| GW Guinea-Bissau | Latin | L | 5 | 5 | 15 |
| GY Guyana | Latin | H | 5 | 5 | 10 |
| HT Haiti | Latin | LM | 12 | 12 | 12 |
| HN Honduras | Latin | LM | 11 | 11 | 12 |
| HK Hong Kong | Han | H | 15 | 15 | 15 |
| HU Hungary | Latin | H | 10 | 10 | 10 |
| IS Iceland | Latin | H | 10 | 10 | 10 |
| IN India | Devanagari | LM | 15 | 15 | 15 |
| ID Indonesia | Latin | UM | 12 | 11 | 12 |
| IR Iran | Arabic | UM | 15 | 15 | 15 |
| IQ Iraq | Arabic | UM | 15 | 15 | 15 |
| IE Ireland | Latin | H | 10 | 10 | 10 |
| IL Israel | Hebrew | H | 15 | 15 | 15 |
| IT Italy | Latin | H | 10 | 10 | 10 |
| CI Ivory Coast | Latin | LM | 12 | 12 | 12 |
| JM Jamaica | Latin | UM | 4 | 4 | 12 |
| JP Japan | Japanese | H | 15 | 15 | 15 |
| JO Jordan | Arabic | LM | 15 | 15 | 15 |
| KZ Kazakhstan | Cyrillic | UM | 15 | 15 | 15 |
| KE Kenya | Latin | LM | 12 | 12 | 12 |
| KI Kiribati | Latin | LM | 2 | 2 | 12 |
| XK Kosovo | Latin | UM | 12 | 12 | 12 |
| KW Kuwait | Arabic | H | 15 | 15 | 15 |
| KG Kyrgyzstan | Cyrillic | LM | 11 | 11 | 15 |
| LA Laos | Lao | LM | 15 | 15 | 15 |
| LV Latvia | Latin | H | 10 | 10 | 10 |
| LB Lebanon | Arabic | LM | 15 | 15 | 15 |
| LS Lesotho | Latin | LM | 3 | 3 | 12 |
| LR Liberia | Latin | L | 4 | 4 | 15 |
| LY Libya | Arabic | UM | 4 | 4 | 15 |
| LI Liechtenstein | Latin | H | 8 | 8 | 10 |
| LT Lithuania | Latin | H | 10 | 10 | 10 |
| LU Luxembourg | Latin | H | 10 | 10 | 10 |
| MO Macau | Han | H | 15 | 15 | 15 |
| MG Madagascar | Latin | L | 15 | 15 | 15 |
| MW Malawi | Latin | L | 7 | 7 | 15 |
| MY Malaysia | Latin | UM | 12 | 12 | 12 |
| MV Maldives | Thaana | UM | 6 | 6 | 15 |
| ML Mali | Latin | L | 2 | 2 | 15 |
| MT Malta | Latin | H | 10 | 10 | 10 |
| MH Marshall Islands | Latin | UM | 0 | 0 | 12 |
| MR Mauritania | Arabic | LM | 8 | 8 | 15 |
| MU Mauritius | Latin | UM | 10 | 10 | 12 |
| MX Mexico | Latin | UM | 12 | 12 | 12 |
| FM Micronesia | Latin | LM | 3 | 3 | 12 |
| MD Moldova | Latin | UM | 12 | 12 | 12 |
| MC Monaco | Latin | H | 10 | 10 | 10 |
| MN Mongolia | Cyrillic | UM | 15 | 15 | 15 |
| ME Montenegro | Cyrillic | UM | 15 | 15 | 15 |
| MA Morocco | Arabic | LM | 15 | 15 | 15 |
| MZ Mozambique | Latin | L | 7 | 7 | 15 |
| MM Myanmar | Burmese | LM | 15 | 15 | 15 |
| NA Namibia | Latin | UM | 12 | 12 | 12 |
| NR Nauru | Latin | H | 0 | 0 | 10 |
| NP Nepal | Devanagari | LM | 15 | 15 | 15 |
| NL Netherlands | Latin | H | 10 | 10 | 10 |
| NZ New Zealand | Latin | H | 10 | 10 | 10 |
| NI Nicaragua | Latin | LM | 12 | 12 | 12 |
| NE Niger | Latin | L | 5 | 5 | 15 |
| NG Nigeria | Latin | LM | 12 | 12 | 12 |
| KP North Korea | Hangul | L | 2 | 2 | 15 |
| MK North Macedonia | Cyrillic | UM | 15 | 15 | 15 |
| NO Norway | Latin | H | 10 | 10 | 10 |
| OM Oman | Arabic | H | 15 | 15 | 15 |
| PK Pakistan | Arabic | LM | 15 | 15 | 15 |
| PW Palau | Latin | H | 3 | 0 | 10 |
| PS Palestine | Arabic | LM | 15 | 15 | 15 |
| PA Panama | Latin | H | 10 | 10 | 10 |
| PG Papua New Guinea | Latin | LM | 0 | 0 | 12 |
| PY Paraguay | Latin | UM | 12 | 12 | 12 |
| PE Peru | Latin | UM | 12 | 12 | 12 |
| PH Philippines | Latin | LM | 12 | 12 | 12 |
| PL Poland | Latin | H | 10 | 10 | 10 |
| PT Portugal | Latin | H | 10 | 10 | 10 |
| QA Qatar | Arabic | H | 15 | 15 | 15 |
| CG Republic of the Congo | Latin | LM | 6 | 6 | 12 |
| RO Romania | Latin | H | 10 | 10 | 10 |
| RU Russia | Cyrillic | H | 15 | 15 | 15 |
| RW Rwanda | Latin | L | 11 | 11 | 15 |
| KN Saint Kitts and Nevis | Latin | H | 10 | 10 | 10 |
| LC Saint Lucia | Latin | UM | 1 | 1 | 12 |
| VC Saint Vincent and the Grenadines | Latin | UM | 5 | 5 | 12 |
| WS Samoa | Latin | LM | 2 | 2 | 12 |
| SM San Marino | Latin | H | 10 | 10 | 10 |
| ST Sao Tome and Principe | Latin | LM | 1 | 1 | 12 |
| SA Saudi Arabia | Arabic | H | 15 | 15 | 15 |
| SN Senegal | Latin | LM | 8 | 8 | 12 |
| RS Serbia | Cyrillic | UM | 15 | 15 | 15 |
| SC Seychelles | Latin | H | 4 | 4 | 10 |
| SL Sierra Leone | Latin | L | 2 | 2 | 15 |
| SG Singapore | Latin | H | 10 | 10 | 10 |
| SK Slovakia | Latin | H | 10 | 10 | 10 |
| SI Slovenia | Latin | H | 10 | 10 | 10 |
| SB Solomon Islands | Latin | LM | 7 | 7 | 12 |
| SO Somalia | Latin | L | 5 | 5 | 15 |
| ZA South Africa | Latin | UM | 12 | 12 | 12 |
| KR South Korea | Hangul | H | 15 | 15 | 15 |
| SS South Sudan | Latin | L | 0 | 0 | 15 |
| ES Spain | Latin | H | 10 | 10 | 10 |
| LK Sri Lanka | Sinhala | LM | 15 | 15 | 15 |
| SD Sudan | Arabic | L | 5 | 5 | 15 |
| SR Suriname | Latin | UM | 12 | 12 | 12 |
| SE Sweden | Latin | H | 10 | 10 | 10 |
| CH Switzerland | Latin | H | 10 | 10 | 10 |
| SY Syria | Arabic | L | 13 | 13 | 15 |
| TW Taiwan | Han | H | 15 | 15 | 15 |
| TJ Tajikistan | Cyrillic | LM | 5 | 5 | 15 |
| TZ Tanzania | Latin | LM | 12 | 12 | 12 |
| TH Thailand | Thai | UM | 15 | 15 | 15 |
| TL Timor-Leste | Latin | LM | 5 | 5 | 12 |
| TG Togo | Latin | L | 15 | 15 | 15 |
| TO Tonga | Latin | UM | 5 | 5 | 12 |
| TT Trinidad and Tobago | Latin | H | 8 | 8 | 10 |
| TN Tunisia | Arabic | LM | 15 | 15 | 15 |
| TR Turkey | Latin | UM | 12 | 12 | 12 |
| TM Turkmenistan | Latin | UM | 4 | 4 | 12 |
| TV Tuvalu | Latin | UM | 4 | 4 | 12 |
| UG Uganda | Latin | L | 15 | 15 | 15 |
| UA Ukraine | Cyrillic | UM | 15 | 15 | 15 |
| AE United Arab Emirates | Arabic | H | 15 | 15 | 15 |
| GB United Kingdom | Latin | H | 10 | 10 | 10 |
| US United States | Latin | H | 10 | 10 | 10 |
| UY Uruguay | Latin | H | 10 | 10 | 10 |
| UZ Uzbekistan | Latin | LM | 12 | 12 | 12 |
| VU Vanuatu | Latin | LM | 12 | 12 | 12 |
| VA Vatican City | Latin | H | 4 | 4 | 10 |
| VE Venezuela | Latin | UM | 12 | 12 | 12 |
| VN Vietnam | Latin | LM | 12 | 12 | 12 |
| YE Yemen | Arabic | L | 7 | 7 | 15 |
| ZM Zambia | Latin | LM | 12 | 12 | 12 |
| ZW Zimbabwe | Latin | LM | 8 | 8 | 12 |

**No photos yet (8):** Chad, Comoros, DR Congo, Equatorial Guinea, Marshall Islands, Nauru, Papua New Guinea, South Sudan

