# CAT Studio

A browser-local CAT exam workspace with JSON imports, timed sectionals, full mocks, and persistent attempt analysis.

## Start

Double-click **Start CAT Studio.cmd**, or run `npm start` in this folder, then open **http://localhost:4173** in Chrome or Edge. Node.js 24 is available on this machine. Keep the server terminal open while using the app. There are no runtime package dependencies or external network requests.

Use the same browser profile and address each time: `localhost` and `127.0.0.1` have separate browser storage. The old `cat_sectional_practice.html` redirects to the new dashboard; its original contents are preserved under `archive/`.

## Included content

- `samples/varc-section-6.json`: 24 questions extracted from `VA sectional 6.zip`, with 4 RC passages, 8 standalone verbal questions, and 4 TITA questions. Source question numbers and screenshot filenames are retained. Keys come from green correct-option indicators or explicit TITA answer fields, not previous selections. Question 11 appeared in the last screenshot and has been restored to its correct place.
- `samples/sample-full-mock.json`: 9 original demo questions across VARC, DILR and QA. It demonstrates grouping, question types, topics and explanations; it is not a full-size CAT paper.
- Both tests are added to a new browser library automatically. No solution explanations were visible in the supplied ZIP; review screens explicitly say when an explanation is unavailable.

## Use

1. Send question/answer screenshots as a ZIP in chat for extraction and verification.
2. Choose **Import test**, upload the prepared JSON or paste it, then validate and confirm the preview.
3. Start a sectional, or use **Build a full mock** to combine one section from each source. A full mock runs VARC → DILR → QA in three consecutive 40-minute windows.
4. Optionally shuffle groups. Questions within a passage/set and option order remain unchanged.
5. **Save & Next** or **Mark for Review & Next** commits a response. Palette/Previous navigation discards an unsaved selection when returning to that question. Clear Response removes the saved response; a review flag can remain. Saved-and-reviewed answers are scored.
6. Review raw scores, section/set results, question times, visits, answer changes, topics and trends. Filter history/progress by section, test, dates, first attempts or retakes.
7. **Export backup** regularly. **Restore backup** merges new records without overwriting existing attempts. Individual attempt exports use the same restorable format. A running-attempt backup retains its original deadlines and can be restored when there is no local active attempt.

## Rules and timing

- MCQ: +3 correct, −1 incorrect, 0 unanswered. TITA: +3 correct, 0 incorrect/unanswered. TITA uses numeric equality across explicit accepted answer strings (`9` and `9.0` are equivalent).
- No early section switching or submission. At the deadline, already-saved responses are scored and the next section starts. Unsaved drafts are not scored.
- Refreshes, tab changes and browser closure do not stop the exam clock. Reopening after several deadlines skips elapsed sections; after 120 minutes, a full mock is completed.
- IndexedDB stores immutable test snapshots, responses, events and millisecond timing. Responses persist after interaction; timing checkpoints run every second. A sudden process/device failure can lose the last uncommitted transaction, usually at most the final timing checkpoint.
- Question time is visible-tab viewing time summed across visits. Hidden time and long heartbeat gaps (>2.5 seconds, such as sleep) are away/unobserved time. Shared-passage reading counts towards the question visible at the time; set totals sum those intervals once. These measurements describe interaction, not thinking.
- Web Locks permit only one editing exam tab per browser profile. Different browsers/devices have separate local data.
- Fixed wall-clock deadlines govern the timer; backward readings are clamped and detected reversals flagged. This personal practice tool is not tamper-proof against system-clock manipulation. Proctored exams would need a server clock.
- Scores are raw practice scores. No invented percentiles or official normalization is applied.

## JSON contract

See `samples/sample-full-mock.json` for a complete example and `test-format.schema.json` for the format. The runtime validator also enforces cross-references and ID uniqueness.

```json
{
  "schemaVersion": 1,
  "id": "my-varc-test",
  "revision": 1,
  "title": "My VARC sectional",
  "sections": [{
    "code": "VARC",
    "groups": [{
      "id": "rc-1",
      "title": "Reading passage 1",
      "stimulus": "Shared passage text.",
      "questions": [{
        "id": "q1",
        "type": "MCQ",
        "prompt": "Question text",
        "options": [
          {"id": "A", "text": "First option"},
          {"id": "B", "text": "Second option"},
          {"id": "C", "text": "Third option"},
          {"id": "D", "text": "Fourth option"}
        ],
        "answer": "B",
        "topic": "Reading comprehension",
        "explanation": "Optional explanation."
      }]
    }]
  }]
}
```

TITA questions omit `options` and use `"type": "TITA", "answer": ["42"]`. Each standalone question gets its own group. MCQ answers are stable option IDs, never display indexes. DILR is the canonical code for LRDI. IDs should be stable; group/question IDs must be unique across the test. Increase `revision` to update a test. Existing attempts retain the original content.

Use Unicode for mathematical notation. Diagrams, complex tables and equations can use embedded images. Attach `assetIds` to a group or question and define assets at the root: `"assets": {"figure-1": {"alt": "Description", "data": "data:image/png;base64,..."}}`. Only embedded PNG, JPEG and WebP images are accepted. Arbitrary HTML and scripts are displayed as text; external image URLs are rejected. The import UI limits JSON files to 30 MB.

For DILR graphs/charts, use only a legible crop of the original source image, preserving axes, legends, labels and units. Embed it as an asset on the relevant set (or question). Do not transcribe graph values into the stimulus or alt text, convert the graph to a table, or recreate it using HTML, SVG, canvas or another visualization. Keep the surrounding set instructions, conditions, questions and options as text. Use a short descriptive alt label without extracted values. If the source graph is unreadable, request a clearer image instead of reconstructing it. Apply this rule to both sectionals and full mocks, including question review.

The previous prototype's unversioned arrays are not this import format. Timing and scoring are fixed application rules; importing different duration/scoring fields does not change them. Small papers are supported and shown with their actual question count, but still run for 40 minutes per section.

## Development and verification

- `npm test`: engine tests using Node's built-in runner.
- `npm run test:browser`: Playwright checks against the running local server using installed Chrome and isolated temporary profiles. Run `npm install` for development dependencies if needed. Tests do not touch normal browser data.
- `node scripts/bundle.js`: rebuild bundled content from reviewed VARC JSON and original demo definitions.
- `scripts/extract_source.py` and `scripts/build_data.py`: OCR preparation/reconstruction aids for this screenshot layout. Require Python, Pillow and Tesseract; these are not a general-purpose automatic ZIP importer. Screenshots and OCR work files are excluded from the app server.
- `test-results/`: generated browser screenshots and backup used for testing.

There is no hosted deployment, account backend, or cloud sync. Clearing site data removes local history; exported backups provide recovery.

## Detailed analysis and supplied reference data

Open **View supplied source analysis** on VARC Section Test 6 to view the original IMS screenshot result. Revision 2 upgrades automatically on refresh; existing attempts keep their original questions and responses. Identical older questions can display newly supplied benchmark metadata without changing scores.

Analysis has Scorecard, Area-wise, Question-wise and Question selection views, plus passage/set totals, answer review, filters, sorting and saved attempt timelines. Accuracy uses correct / attempted; time per attempt includes time on skipped questions. Zero denominators display a dash. Source A/B/C categories are preserved, not inferred from difficulty or answer format.

The supplied result is 1 mark, 15 attempted, 3 correct and 20% accuracy. Question times sum to 39:47. Original provider area figures are retained separately because their displayed averages differ from recomputing rounded question times. Source percentile 17.1 and the supplied mapper apply only to that original result. No percentile is estimated for new attempts. Topper p-values and other benchmarks appear only when supplied in JSON, with provenance; missing values remain blank. Source choices and visit history are unknown and are not invented.

## Full mock from images

1. Send a ZIP in chat with folders `VARC`, `DILR` (or LRDI), and `QA`. Include complete passages/sets, questions, options, answer keys and any solution or analysis images. Label source question numbers consistently across images.
2. Request one JSON using `test-format.schema.json`, with `testType: "full"` and all three sections. Use globally unique question/group IDs, shared `stimulus` and one group per RC/DILR set. Transcribe supplied benchmarks only; omit unavailable fields. Resolve unreadable answers before importing.
3. In **Import test**, select **Full mock** and paste/upload the JSON. Review section counts, then add it to the library. There is no need to compose sectionals first. `samples/sample-full-mock.json` is a downloadable original demo of this format, not an extracted real mock.
4. Start the full mock: VARC ? DILR ? QA, 40 minutes each. Group shuffling preserves questions within sets.

The browser imports JSON; ZIP image extraction happens in chat. DILR Sectional 1 and SimCAT 2 have also been imported from the supplied ZIPs.

Optional question metadata: `area`, `selectionCategory` (A/B/C), and `benchmark` with required `source` plus optional `sourceImage`, `topperTimeSeconds`, `topperAttemptPercent`, `topperAccuracyPercent`, `topperPValue`. Percentages must be within 0–100. Root `sourceAnalysis` stores a separately labelled reference result with `sourceImages` and `questionResults` mapped by stable question ID. See the updated VARC JSON for a complete example.

To regenerate bundled data after the original extraction: `python scripts/build_data.py`, then `python scripts/add_varc_analytics.py`, then `node scripts/bundle.js`. Run `npm test` and `npm run test:browser` (requires local server and Chrome).



## DILR Sectional 1 and SimCAT 2

Refresh the app to add the bundled tests. Import-ready files: `samples/dilr-section-1.json` (22 questions, five sets) and `samples/simcat-2.json` (24 VARC + 22 DILR + 22 QA). Answer keys, original set order, source question numbers and visible A/B/C categories and topper benchmarks are preserved. Tables are transcribed and embedded as cropped source images; the school admissions chart is embedded too. Missing/cut-off statistics are omitted. These ZIPs do not provide a complete timed original attempt, so no synthetic source scorecard or percentile is created. Fresh attempts support all four analysis views.

To reuse a full mock:
- Start test and select one section for a 40-minute attempt.
- Use **Save a section as a separate test** on the full-mock card to save it to your library or download its JSON.
- Use **Build a full mock** to select VARC, DILR and QA independently from any sectional or full mock. For example, SimCAT 2 VARC + DILR Sectional 1 + SimCAT 2 QA. Sets, answer keys, assets and benchmarks are copied without changing source tests or past attempts.

Rebuild the reviewed new imports with `python scripts/build_new_imports.py`, then `node scripts/bundle.js`. The OCR intermediates in `extraction` are local extraction aids. `npm run test:new-imports` checks section extraction, download, mixed-source composition, real DILR content, embedded images and analytics in Chrome with the local server running.

## SimCAT 3, Take Home 1 and SimCAT 4

`samples/simcat-3.json`, `samples/take-home-1.json` and `samples/simcat-4.json` are standalone full-mock imports from the supplied ZIPs. Take Home 1 is labelled SimCAT 101 in its source screenshots. Each contains 24 VARC, 22 DILR and 22 QA questions, four intact RC passages, five intact DILR sets, answer keys, and source benchmarks. DILR graphs are embedded only as original image crops; original tables and the QA geometry figure are embedded where present. The files work with section extraction and the custom-mock builder.

Each file includes a separate original-attempt analysis, with the supplied question outcomes and times. SimCAT 3 reconciles to 20 marks (13 VARC, 2 DILR, 5 QA); Take Home 1 reconciles to 22 marks (17 VARC, 3 DILR, 2 QA); SimCAT 4 reconciles to 26 marks (18 VARC, 5 DILR, 3 QA). Source percentiles and reference values are retained only from the supplied screenshots and are never assigned to a new attempt. Provider question times are preserved even where their total differs from a strict 40-minute section.

Import either JSON on an existing hosted dashboard, or refresh the updated local app to load both bundled tests. Rebuild reviewed data using `python scripts/build_oct13_imports.py` and `node scripts/bundle.js`; this requires the local extraction intermediates. Run `npm test` and, with the local server running, `node tests/oct13-imports.cjs` for browser verification.


## Take Home 2 (SimCAT 102)

`samples/take-home-2.json` is the full mock imported from TakeHome 2.zip and included in the bundled library. It contains 24 VARC, 22 DILR and 22 QA questions, with four RC passages and five DILR sets. Original graph/table images and the original QA 21 expression are embedded. Sections can be extracted and reused in custom mocks.

The supplied original-attempt analysis reconciles to 41 marks (29 VARC, 9 DILR, 3 QA), with 27 attempts and 16 correct answers. Supplied question timings, A/B/C categories, topper benchmarks, scorecard percentiles and percentile mapper are preserved separately from new attempts.


## Take Home 3 and Take Home 5

Take Home 3 (SimCAT 103) is available as `samples/take-home-3.json` and in the bundled library: 24 VARC, 22 DILR and 22 QA questions. Its source attempt reconciles to 13 marks (11 VARC, 3 DILR, -1 QA). RC and DILR groups remain intact when shuffling or extracting sections.

Take Home 5 (SimCAT 105) is available as `samples/take-home-5.json` and in the bundled library, with all 68 questions, supplied analysis and original figures. The six previously hidden DILR answers (1-4 and 21-22) are verified from the follow-up screenshots. Its source attempt reconciles to 47 marks (40 VARC, -1 DILR, 8 QA), with 43 attempts and 18 correct answers. All three sections can be extracted and reused in custom mocks.

For both QA and DILR, figures must be original image crops. Extract surrounding questions/options as text, but do not redraw diagrams, generate SVG/charts, or substitute figure labels/data for the original figure. Crop out answers, selections, browser chrome and unrelated controls.

## Take Home 4 (SimCAT 104)

`samples/take-home-4.json` is imported from `TakeHome 4 DONE.zip` and included in the bundled library. It contains 24 VARC, 22 DILR and 22 QA questions, four RC passages, five intact DILR sets and all 68 verified answer keys. Nine original image assets preserve the DILR figures/tables, admission-call graphs, QA geometry figures and logarithmic expression. The whole-set screenshot supplies the complete admission-call conditions. Sections can be extracted for sectionals and custom mocks.

The ZIP has no separate scorecard. Only 26 questions show both original outcomes and timings: VARC 1–16 and DILR 6–12, 14, 16–17. Source analysis explicitly covers that subset (18 marks), not a full-mock score. Visible benchmarks and categories are retained where supplied; unavailable percentiles, timings and p-values are omitted. Missing source results are excluded from totals. New attempts receive complete analysis for every question.

Rebuild with `python scripts/build_takehome4_import.py` and `node scripts/bundle.js` after preparing the local extraction intermediates.

## Take Home 6 (SimCAT 106)

`samples/take-home-6.json` is imported from `TakeHome 6 DONE.zip` and bundled in the library. It contains 24 VARC, 22 DILR and 22 QA questions, four RC passages, five intact DILR sets, and six original image assets. Sections can be extracted for sectionals and custom mocks; shuffling preserves sets.

The supplied source analysis reconciles to 45 marks (24 VARC, 14 DILR, 7 QA), 33 attempts and 18 correct answers. All 68 source outcomes/timings, supplied categories, benchmarks, percentiles and the percentile mapper are included separately from new attempts. Question timings use the question-wise analysis screenshots consistently. QA area assignments reconcile the source area times and selection matrix.

Rebuild using `python scripts/build_takehome6_import.py` and `node scripts/bundle.js` with the local OCR intermediates available. Run `npm test`; browser verification uses `node tests/takehome6-import.cjs` with the app served on port 4173.

## SimCAT 5

`samples/simcat-5.json` is the completed 68-question import from `SimCAT 5 DONE.zip`, included in the bundled library. Follow-up screenshots confirm VARC Q20 = D and Q24 option D = Option 1. Four RC passages and five DILR sets retain their source order, and the original bonus table and QA series expression are embedded. Sections can be extracted and reused in custom mocks.

Source analysis reconciles to 35 marks (30 VARC, 5 DILR, 0 QA), 20 attempts and 13 correct answers, with 68 supplied outcomes/timings. Source selection totals and area classifications are preserved; no percentile is invented. New attempts do not inherit source results.

Rebuild using `python scripts/build_simcat5_import.py` and `node scripts/bundle.js` with the local OCR intermediates available. Checks: `npm test` and `node tests/simcat5-import.cjs` (local server on port 4173).
