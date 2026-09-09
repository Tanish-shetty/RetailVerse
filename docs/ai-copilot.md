# RetailIQ Copilot

Question → controlled intent → validated filters → repository → analytical operation →
structured evidence → optional Groq recommendation → structured response.

Supported operations: trends, product performance, region/state comparisons, RFM rankings,
promotion summaries, forecasts and anomaly candidates. Known names are resolved against the
dataset; explicit quarters and years, or full month names, can constrain dates. Without a
year, a named month/quarter uses the latest dataset year and reports that assumption.
“Last month” currently refers to the latest observed trend month and its prior month, not
the wall-clock month; the answer explicitly says latest observed month. Use a date filter
or explicit month/year for precision. Free-form arbitrary SQL, unrestricted joins and
arbitrary natural-language date expressions are outside scope. UI filters remain the most
precise way to scope questions. Do not treat the keyword router as universal language understanding.

The backend never executes model-generated SQL or code. A small operation allowlist selects
existing Python functions; SQL filters are parameterized. Dangerous/unsupported requests
receive a safe response. The runtime database account must be SELECT-only. Only relevant
aggregates/top records are sent to Groq, never credentials or a full database dump.

Response fields: answer, key_metrics, supporting_evidence, recommendation, caveats, mode.
Numerical answers are computed deterministically. Groq only drafts a recommendation, which
is checked for valid JSON, string type, bounded length and absence of numeric digits.
This check does not prove semantic grounding; review generated recommendations as advice,
not verified facts. Keys and model names are configured with GROQ_API_KEY / GROQ_MODEL.
Without a key, on timeout, on provider failure, or malformed output, computed evidence and
a deterministic recommendation remain available. No paid API call is made in tests.

Implementation references: [Groq text generation](https://console.groq.com/docs/text-chat)
and [JSON output semantics](https://console.groq.com/docs/structured-outputs).
JSON object mode guarantees neither our schema nor correctness, so the application validates
the returned object. Users should not enter personal or secret data into the question box.
