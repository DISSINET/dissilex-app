# NOTICE — Third-Party Data in DISSILEX

This NOTICE accompanies the DISSILEX dataset (`data/dissilex.db`) and must be
retained with **all copies** of that dataset, as required by the licences below.

The DISSILEX dataset is licensed under **CC BY-SA 4.0**
(<https://creativecommons.org/licenses/by-sa/4.0/>; see `LICENSE-DATA`).
The DISSILEX application code is licensed separately under **BSD 3-Clause**
(see `LICENSE`).

The dataset incorporates and redistributes material from the external resources
below. Each is used under its own licence; those licences continue to govern the
respective portions of the data regardless of the CC BY-SA 4.0 licence on the
dataset as a whole.

---

## LiLa Lemma Bank — CC BY-SA 4.0

CIRCSE, Università Cattolica del Sacro Cuore (supervised by Marco Carlo
Passarotti). DISSILEX redistributes a subset of LiLa standard lemma forms and
part-of-speech labels (identifiers and canonical forms; no further LiLa data) in
reformatted form. This LiLa-derived portion remains under CC BY-SA 4.0; no lemma
data was modified beyond format conversion and selection.

Mambrini, F. and Passarotti, M.C. (2023). *The LiLa Lemma Bank: A Knowledge Base
of Latin Canonical Forms.* Journal of Open Humanities Data 9(1).
<https://doi.org/10.5334/johd.145>

<https://lila-erc.eu/>

---

## Princeton WordNet 3.0 / 3.1 — WordNet License

Princeton University. DISSILEX redistributes Princeton WordNet synset identifiers
for versions 3.0 and 3.1, including **glosses (definitions)** for version 3.0. 
WordNet relations are not stored. Princeton issues a single licence covering 
both versions. "Princeton University" is not used to endorse or promote DISSILEX.

The full copyright notice and statements, including the disclaimer, are
reproduced verbatim below as the licence requires on all copies:

> WordNet Release 3.0 This software and database is being provided to you, the
> LICENSEE, by Princeton University under the following license. By obtaining,
> using and/or copying this software and database, you agree that you have read,
> understood, and will comply with these terms and conditions.: Permission to
> use, copy, modify and distribute this software and database and its
> documentation for any purpose and without fee or royalty is hereby granted,
> provided that you agree to comply with the following copyright notice and
> statements, including the disclaimer, and that the same appear on ALL copies of
> the software, database and documentation, including modifications that you make
> for internal use or for distribution. WordNet 3.0 Copyright 2006 by Princeton
> University. All rights reserved. THIS SOFTWARE AND DATABASE IS PROVIDED "AS IS"
> AND PRINCETON UNIVERSITY MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR
> IMPLIED. BY WAY OF EXAMPLE, BUT NOT LIMITATION, PRINCETON UNIVERSITY MAKES NO
> REPRESENTATIONS OR WARRANTIES OF MERCHANT- ABILITY OR FITNESS FOR ANY
> PARTICULAR PURPOSE OR THAT THE USE OF THE LICENSED SOFTWARE, DATABASE OR
> DOCUMENTATION WILL NOT INFRINGE ANY THIRD PARTY PATENTS, COPYRIGHTS, TRADEMARKS
> OR OTHER RIGHTS. The name of Princeton University or Princeton may not be used
> in advertising or publicity pertaining to distribution of the software and/or
> database. Title to copyright in this software, database and any associated
> documentation shall at all times remain with Princeton University and LICENSEE
> agrees to preserve same.

WordNet 3.0 was accessed via NLTK; WordNet 3.1 via the LiLa SPARQL endpoint.

Citations:

Fellbaum, C. (1998) *WordNet: An electronic lexical database.* MIT press.

Miller, G. A. (1995). *WordNet: A Lexical Database for English.* Communications
of the ACM 38(11): 39–41. Fellbaum, C. (ed.) (1998). *WordNet: An Electronic
Lexical Database.* MIT Press.

Princeton University. (2010) *What is WordNet?* URL: <https://wordnet.princeton.edu/>.
Accessed: 2 June 2026.

---

## CILI — Collaborative Interlingual Index — CC BY 4.0

Open Multilingual Wordnet (OMW). DISSILEX uses the Princeton WordNet 3.0 ↔ 3.1
offset mappings (`ili-map-pwn30.tab`, `ili-map-pwn31.tab`) **at build time only**
to bridge WordNet versions. The CILI tables are **not redistributed** with the
DISSILEX code or dataset; they are obtained directly from the source below. CILI
is credited here for transparency.

Bond, F., Vossen, P., McCrae, J., Fellbaum, C. (2016). *CILI: the Collaborative
Interlingual Index.* Proceedings of the 8th Global WordNet Conference, 50–57.
<https://aclanthology.org/2016.gwc-1.9/>

<https://github.com/globalwordnet/cili>

---

## Latin WordNet — not redistributed

University of Exeter, William Michael Short; revised by the CIRCSE research
group. Licensed under CC BY-NC-SA 4.0. DISSILEX does **not** redistribute any
Latin WordNet data; it only reports, for analysis, which Latin Actions and
Concepts overlap with Latin WordNet synsets (computed via the LiLa SPARQL
endpoint). No CC BY-NC-SA content is included in the dataset.

<https://latinwordnet.exeter.ac.uk/>
