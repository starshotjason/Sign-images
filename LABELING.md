# Reviewing and transcribing staged photos

You review photos for a sign-reader test set (format: jasontitus/streetzim `docs/ocr-test-set.md`,
a copy is at `/home/user/jasontitus/streetzim/docs/ocr-test-set.md`; real labelled examples are in
`/home/user/jasontitus/streetzim/tests/fixtures/ocr-signs/manifest.jsonl`). A phone app photographs a
sign, reads its text (OCR), and searches an offline map for the place. Each photo needs a
ground-truth label.

## Inputs, for a country code `cc` (lowercase ISO 3166-1)

- `review/<cc>/<key>.jpg`: a 1600 px preview of each staged photo. Look at it with the Read tool.
- `staging/<cc>/<key>.cand.json`: source metadata (title, categories, description, licence). Use the
  title, categories and description as hints for what the sign says and where it is, but label only
  what you can actually see.

## Output: `labels/<cc>.json`

Write one JSON object keyed by `<key>` (the file name without its extension). Write only the countries
you were assigned. If the file already exists, merge into it and keep existing entries.

```json
{
  "c12345678": {
    "accept": true,
    "reason": "",
    "kind": "street sign",
    "scripts": ["Arab", "Latn"],
    "lines": [
      {"text": "شارع الجمهورية", "lang": "ar", "latin": "Shari' al-Jumhuriya (Republic Street)"},
      {"text": "Gomhoreya St.", "lang": "en"}
    ],
    "expect": {"query": "Gomhoreya", "type": "street"},
    "difficulty": "easy",
    "notes": "Blue enamel plate; the shop signs behind it are distractors."
  },
  "f1a2b3": {"accept": false, "reason": "no readable sign text"}
}
```

## Accept only when all of these hold

- It is a real photograph, not a map, drawing, scan, logo, document, product or screenshot.
- One main sign or name panel is the target, and its text is legible at 1600 px: a street-name plate,
  address or house-number plate, building or lane tag, a shop, restaurant, hotel, bank or pharmacy
  sign, a landmark name board (museum, temple, mosque, school, station, park, ministry), or a
  transit stop or station sign. Directional road signs naming places are fine (kind "landmark" or
  "street sign", whichever fits best). Pure traffic pictograms with no place text are not.
- The sign names something a map could contain: a street, place, business, building or stop. Slogans,
  advertising copy, warnings ("No parking"), menus and graffiti alone are rejected.
- No person's face or vehicle number plate is the subject. People incidental in a street scene are fine.
- No stock-photo watermark across the image.
- It is not a near-duplicate of another photo you accepted for the same country.

Prefer variety: aim for a mix of kinds per country. Accept generously when the sign is clear. The
pipeline uses the first N accepted photos by rank, so accepting a few extras is good.

## Fields for accepted photos

- `kind`: one of `street sign`, `address plate`, `building tag`, `business sign`, `landmark`,
  `transit`, `bilingual` (use it only when no other kind fits better and the sign is in two scripts),
  `hard` (very far, angled, night, partly hidden, handwritten), or `negative`. Use `negative` when the
  only text is in a script the reader cannot handle yet (Hebrew, Georgian, Armenian, Ethiopic, Bengali,
  Gurmukhi, Gujarati, Oriya, Kannada, Malayalam, Sinhala, Khmer, Lao, Burmese, Tibetan, Thaana,
  Tifinagh) with no Latin text. Still transcribe those lines.
- `scripts`: ISO 15924 codes of the target sign's text (Latn, Arab, Cyrl, Grek, Hebr, Geor, Armn,
  Ethi, Deva, Beng, Taml, Telu, Sinh, Thai, Laoo, Khmr, Mymr, Tibt, Thaa, Hani, Hira, Kana, Hang,
  Tfng, Zyyy for digits only).
- `lines`: the target sign's text, line by line in reading order, exactly as written, keeping the
  original digits (Arabic-Indic, Persian, Devanagari, ...). Each line has `lang` (ISO 639-1 where
  possible, `und` for numbers alone). Non-Latin lines also need `latin`: a romanisation, with a short
  translation in brackets when helpful. Do not invent characters you cannot read: transcribe the
  legible part and say what is missing in `notes`.
- `expect.query`: what a person would type into the map's search to find the target, usually the
  street or place name in the local spelling (or its Latin form if that is what the sign shows best).
  `expect.type`: `street`, `poi`, `place`, `addr` or `stop`.
- `difficulty`: `easy` (frontal, close, sharp), `medium`, or `hard`.
- `notes`: anything that helps a checker, such as the address format, distractor signs, or a partial read.

Work through every staged photo for your countries. When you finish, reply with one line per
country: `cc: accepted N / reviewed M`, plus any concerns.
