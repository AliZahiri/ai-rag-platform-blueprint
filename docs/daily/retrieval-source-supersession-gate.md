# Add retrieval source supersession gate

<!-- daily-pr-task: retrieval-source-supersession-gate -->

Replacing a corpus source requires a traceable relationship rather than an unreviewed deletion. This offline gate validates unique source-to-successor records, rejects self-supersession, requires an approval reference, and prevents a record from being marked active after its effective supersession date. It does not query the index or source content.

## Portfolio Value

Preserves citation and corpus lineage through a reviewed handoff from deprecated source material to its approved successor.

## Validation

Run python3 -m unittest discover -s tests and confirm reviewed inactive superseded sources pass while self-links, missing approval, duplicate sources, and active retired sources fail.
