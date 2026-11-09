# Invented example

`greenhouse_requirements.json` is **invented for this package**. It describes a fictional greenhouse irrigation
controller and is **not data from the study**: it has no relation to the specifications evaluated in the paper and
was not produced by the extraction stage. It only lets you try the pipeline quickly and at negligible cost.

It uses the same format as the requirements input of the pipeline:

- `requirements`: `{category: [requirement, ...]}`; each category produces one SysML v2 model;
- `source`: where the requirements come from (read by the pipeline; `doc` fills the `pdf` column of the results);
- `sha256`: digest of `requirements`, checked when the file is loaded;
- `notice`: states that the file is invented. It is specific to this example; the pipeline ignores it.
