# 06 — CiTO Citation

> Run the pre-flight checklist in `docs/forrt-form-fields.md` § Pre-flight checklist before drafting.

**Description:** *"Declare citations between papers or other works, using Citation Typing Ontology"*

## Field-by-field draft

### Identifier for the citing creative work (text input, required)

URI of the Outcome published in step 05.

```
<paste Outcome URI from PUBLISHED.md step 05 after publishing>
```

### List citations (repeatable group, required ≥1)

This is a question-rooted chain with no original paper to confirm/dispute, so the citations credit the reused method and software and cite the data sources.

#### Citation 1 — the reused Galaxy training/method

##### Citation Type (dropdown)

```
credits
```

##### DOI or other URL of the cited work (text input)

```
https://gxy.io/GTN:T00516
```

#### Citation 2 — the reused CellProfiler software

##### Citation Type (dropdown)

```
credits
```

##### DOI or other URL of the cited work (text input)

```
https://doi.org/10.1371/journal.pbio.2005970
```

#### Citation 3 — input data source

##### Citation Type (dropdown)

```
citesAsDataSource
```

##### DOI or other URL of the cited work (text input)

```
https://nasa-gibs.github.io/gibs-api-docs/
```

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 06. This completes the six-step chain. The optional Research Software nanopub is in `drafts/07_research_software.md`.
