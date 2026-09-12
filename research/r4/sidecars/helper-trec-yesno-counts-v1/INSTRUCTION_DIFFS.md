# Frozen instruction-only verbalizer diffs

Definitions and record text are unchanged.

## human being

```diff
--- literal-target-other
+++ yes-no
@@ -6,6 +6,6 @@
 entity: a nonhuman, nongeographic thing or name, including objects, organisms, works, events, substances, methods or synonymous terms.
 description and abstract concept: a definition, explanation, reason or manner of doing something, rather than a particular name or number.
 numeric value: a quantity, count, measurement, date, duration, rank or numerical code.
-Target category: "human being". For this request, return the target label only when the record belongs to that category under the complete definitions above. Return `other` for every remaining category; `other` is the union of ["location","abbreviation","entity","description and abstract concept","numeric value"], not an additional semantic category. Return one keyed answer for every supplied record.
+Target category: "human being". For this request, return `yes` only when the record belongs to that category under the complete definitions above. Return `no` for every remaining category; `no` is the union of ["location","abbreviation","entity","description and abstract concept","numeric value"], not an additional semantic category. Return one keyed answer for every supplied record.
 Return only one JSON object mapping every supplied id exactly once to one label.
-No missing or extra ids. Allowed labels: ["human being","other"]
+No missing or extra ids. Allowed labels: ["yes","no"]
```

## location

```diff
--- literal-target-other
+++ yes-no
@@ -6,6 +6,6 @@
 entity: a nonhuman, nongeographic thing or name, including objects, organisms, works, events, substances, methods or synonymous terms.
 description and abstract concept: a definition, explanation, reason or manner of doing something, rather than a particular name or number.
 numeric value: a quantity, count, measurement, date, duration, rank or numerical code.
-Target category: "location". For this request, return the target label only when the record belongs to that category under the complete definitions above. Return `other` for every remaining category; `other` is the union of ["human being","abbreviation","entity","description and abstract concept","numeric value"], not an additional semantic category. Return one keyed answer for every supplied record.
+Target category: "location". For this request, return `yes` only when the record belongs to that category under the complete definitions above. Return `no` for every remaining category; `no` is the union of ["human being","abbreviation","entity","description and abstract concept","numeric value"], not an additional semantic category. Return one keyed answer for every supplied record.
 Return only one JSON object mapping every supplied id exactly once to one label.
-No missing or extra ids. Allowed labels: ["location","other"]
+No missing or extra ids. Allowed labels: ["yes","no"]
```

## abbreviation

```diff
--- literal-target-other
+++ yes-no
@@ -6,6 +6,6 @@
 entity: a nonhuman, nongeographic thing or name, including objects, organisms, works, events, substances, methods or synonymous terms.
 description and abstract concept: a definition, explanation, reason or manner of doing something, rather than a particular name or number.
 numeric value: a quantity, count, measurement, date, duration, rank or numerical code.
-Target category: "abbreviation". For this request, return the target label only when the record belongs to that category under the complete definitions above. Return `other` for every remaining category; `other` is the union of ["human being","location","entity","description and abstract concept","numeric value"], not an additional semantic category. Return one keyed answer for every supplied record.
+Target category: "abbreviation". For this request, return `yes` only when the record belongs to that category under the complete definitions above. Return `no` for every remaining category; `no` is the union of ["human being","location","entity","description and abstract concept","numeric value"], not an additional semantic category. Return one keyed answer for every supplied record.
 Return only one JSON object mapping every supplied id exactly once to one label.
-No missing or extra ids. Allowed labels: ["abbreviation","other"]
+No missing or extra ids. Allowed labels: ["yes","no"]
```

## entity

```diff
--- literal-target-other
+++ yes-no
@@ -6,6 +6,6 @@
 entity: a nonhuman, nongeographic thing or name, including objects, organisms, works, events, substances, methods or synonymous terms.
 description and abstract concept: a definition, explanation, reason or manner of doing something, rather than a particular name or number.
 numeric value: a quantity, count, measurement, date, duration, rank or numerical code.
-Target category: "entity". For this request, return the target label only when the record belongs to that category under the complete definitions above. Return `other` for every remaining category; `other` is the union of ["human being","location","abbreviation","description and abstract concept","numeric value"], not an additional semantic category. Return one keyed answer for every supplied record.
+Target category: "entity". For this request, return `yes` only when the record belongs to that category under the complete definitions above. Return `no` for every remaining category; `no` is the union of ["human being","location","abbreviation","description and abstract concept","numeric value"], not an additional semantic category. Return one keyed answer for every supplied record.
 Return only one JSON object mapping every supplied id exactly once to one label.
-No missing or extra ids. Allowed labels: ["entity","other"]
+No missing or extra ids. Allowed labels: ["yes","no"]
```

## description and abstract concept

```diff
--- literal-target-other
+++ yes-no
@@ -6,6 +6,6 @@
 entity: a nonhuman, nongeographic thing or name, including objects, organisms, works, events, substances, methods or synonymous terms.
 description and abstract concept: a definition, explanation, reason or manner of doing something, rather than a particular name or number.
 numeric value: a quantity, count, measurement, date, duration, rank or numerical code.
-Target category: "description and abstract concept". For this request, return the target label only when the record belongs to that category under the complete definitions above. Return `other` for every remaining category; `other` is the union of ["human being","location","abbreviation","entity","numeric value"], not an additional semantic category. Return one keyed answer for every supplied record.
+Target category: "description and abstract concept". For this request, return `yes` only when the record belongs to that category under the complete definitions above. Return `no` for every remaining category; `no` is the union of ["human being","location","abbreviation","entity","numeric value"], not an additional semantic category. Return one keyed answer for every supplied record.
 Return only one JSON object mapping every supplied id exactly once to one label.
-No missing or extra ids. Allowed labels: ["description and abstract concept","other"]
+No missing or extra ids. Allowed labels: ["yes","no"]
```

## numeric value

```diff
--- literal-target-other
+++ yes-no
@@ -6,6 +6,6 @@
 entity: a nonhuman, nongeographic thing or name, including objects, organisms, works, events, substances, methods or synonymous terms.
 description and abstract concept: a definition, explanation, reason or manner of doing something, rather than a particular name or number.
 numeric value: a quantity, count, measurement, date, duration, rank or numerical code.
-Target category: "numeric value". For this request, return the target label only when the record belongs to that category under the complete definitions above. Return `other` for every remaining category; `other` is the union of ["human being","location","abbreviation","entity","description and abstract concept"], not an additional semantic category. Return one keyed answer for every supplied record.
+Target category: "numeric value". For this request, return `yes` only when the record belongs to that category under the complete definitions above. Return `no` for every remaining category; `no` is the union of ["human being","location","abbreviation","entity","description and abstract concept"], not an additional semantic category. Return one keyed answer for every supplied record.
 Return only one JSON object mapping every supplied id exactly once to one label.
-No missing or extra ids. Allowed labels: ["numeric value","other"]
+No missing or extra ids. Allowed labels: ["yes","no"]
```
