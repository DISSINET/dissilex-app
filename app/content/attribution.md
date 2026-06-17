# Attribution

DISSILEX integrates and displays lexical data from several external resources. Each is credited below in accordance with its licence.

The DISSILEX dataset (`dissilex.db`) is distributed under CC BY-SA 4.0 (<https://creativecommons.org/licenses/by-sa/4.0/>): a subset of LiLa lemmas is redistributed and its ShareAlike clause applies to the whole dataset.

**Disclaimer:** The material is provided "as is", without warranties of any kind. The creators and contributors of the external resources below do not endorse DISSILEX or its use, and are not responsible for any modifications made within this dataset.

## LiLa Lemma Bank

CIRCSE, Università Cattolica del Sacro Cuore (supervised by Marco Carlo Passarotti). Licensed under CC BY-SA 4.0. DISSILEX uses LiLa standard lemma forms and part-of-speech labels for Latin Actions and Concepts, resolved via the LiLa SPARQL endpoint. A subset of LiLa lemmas is redistributed in reformatted form within the DISSILEX dataset; this LiLa-derived portion remains under CC BY-SA 4.0. No lemma data was modified beyond format conversion and selection.

Citation: Mambrini, F. and Passarotti, M.C. (2023). *The LiLa Lemma Bank: A Knowledge Base of Latin Canonical Forms.* Journal of Open Humanities Data 9(1). <https://doi.org/10.5334/johd.145>

LiLa: Linking Latin has received funding from the European Research Council (ERC) under the European Union's Horizon 2020 research and innovation programme — Grant Agreement No. 769994.

<https://lila-erc.eu/>

## Princeton WordNet 3.0 / 3.1

Princeton University. Licensed under the WordNet License (<https://wordnet.princeton.edu/license-and-commercial-use>). DISSILEX links Concepts and Actions to Princeton WordNet synsets (versions 3.0 and 3.1) where applicable. The redistributed dataset stores synset identifiers and their glosses (definitions); WordNet relations are not stored. The gloss text is reproduced under the WordNet License, whose copyright notice and disclaimer (reproduced verbatim below, as the licence requires on all copies) cover this use. Princeton issues a single licence covering both versions; there is no separate WordNet 3.1 licence. "Princeton University" is not used to endorse or promote DISSILEX.

The full copyright notice and statements, including the disclaimer, reproduced verbatim as the licence requires:

> WordNet Release 3.0 This software and database is being provided to you, the LICENSEE, by Princeton University under the following license. By obtaining, using and/or copying this software and database, you agree that you have read, understood, and will comply with these terms and conditions.: Permission to use, copy, modify and distribute this software and database and its documentation for any purpose and without fee or royalty is hereby granted, provided that you agree to comply with the following copyright notice and statements, including the disclaimer, and that the same appear on ALL copies of the software, database and documentation, including modifications that you make for internal use or for distribution. WordNet 3.0 Copyright 2006 by Princeton University. All rights reserved. THIS SOFTWARE AND DATABASE IS PROVIDED "AS IS" AND PRINCETON UNIVERSITY MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR IMPLIED. BY WAY OF EXAMPLE, BUT NOT LIMITATION, PRINCETON UNIVERSITY MAKES NO REPRESENTATIONS OR WARRANTIES OF MERCHANT- ABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF THE LICENSED SOFTWARE, DATABASE OR DOCUMENTATION WILL NOT INFRINGE ANY THIRD PARTY PATENTS, COPYRIGHTS, TRADEMARKS OR OTHER RIGHTS. The name of Princeton University or Princeton may not be used in advertising or publicity pertaining to distribution of the software and/or database. Title to copyright in this software, database and any associated documentation shall at all times remain with Princeton University and LICENSEE agrees to preserve same.

Citations:

Fellbaum, C. (1998) *WordNet: An electronic lexical database.* MIT press.

Miller, G.A. (1995) *WordNet: a lexical database for English.* Communications of the
ACM, 38(11), pp. 39–41. Available at: https://doi.org/10.1145/219717.219748.

Princeton University. (2010) *What is WordNet?* URL: <https://wordnet.princeton.edu/>.
Accessed: 2 June 2026.

WordNet 3.0 was accessed via NLTK; WordNet 3.1 via the LiLa SPARQL endpoint.

<https://wordnet.princeton.edu/>

## Latin WordNet

University of Exeter, William Michael Short; revised by the CIRCSE research group. Licensed under CC BY-NC-SA 4.0. DISSILEX does not redistribute Latin WordNet data; it only reports, for analysis, which of its Latin Actions and Concepts overlap with Latin WordNet synsets (computed via the LiLa SPARQL endpoint).

<https://latinwordnet.exeter.ac.uk/>

## CILI — Collaborative Interlingual Index

Open Multilingual Wordnet (OMW). Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). DISSILEX uses the Princeton WordNet 3.0 ↔ 3.1 offset mappings (`ili-map-pwn30.tab`, `ili-map-pwn31.tab`) **at build time only** to bridge WordNet versions. The CILI tables are **not redistributed** with the DISSILEX code or dataset; they are obtained directly from the source below. CILI is credited here for transparency.

Citation: Bond, F., Vossen, P., McCrae, J., Fellbaum, C. (2016). *CILI: the Collaborative Interlingual Index.* Proceedings of the 8th Global WordNet Conference, 50–57. <https://aclanthology.org/2016.gwc-1.9/>

<https://github.com/globalwordnet/cili>
