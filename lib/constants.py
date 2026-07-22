class Constants:
	# SPECTRABLOG entity type abbreviation → full name
	ENTITY_CLASS_NAMES = {
		'A': 'Action', 'T': 'Territory', 'S': 'Statement', 'R': 'Resource',
		'P': 'Person', 'B': 'Living Being', 'G': 'Group', 'O': 'Object',
		'C': 'Concept', 'L': 'Location', 'V': 'Value', 'E': 'Event',
	}

	# Valency slot abbreviation → full name
	SLOT_NAMES = {'s': 'Subject', 'a1': 'Actant 1', 'a2': 'Actant 2'}

	# Language code → full name
	LANGUAGE_NAMES = {'lat': 'Latin', 'eng': 'English'}

	# Neo4j relation label → descriptive full name
	RELATION_NAMES = {
		'HAS_SUPERCLASS': 'Superclass',
		'HAS_SYNONYM': 'Synonym',
		'HAS_ANTONYM': 'Antonym',
		'HAS_HOLONYM': 'Holonym',
		'HAS_PROPERTY_RECIPROCAL': 'Property Reciprocal',
		'HAS_SUBJ_A1_RECIPROCAL': 'Subject/Actant1 Reciprocal',
		'HAS_EVENT_EQUIVALENT': 'Action/Event Equivalent',
		'HAS_CLASS': 'Classification',
		'HAS_IMPLICATION': 'Implication',
		'HAS_SUBJ_SEMANTICS': 'Subject Semantics',
		'HAS_A1_SEMANTICS': 'Actant1 Semantics',
		'HAS_A2_SEMANTICS': 'Actant2 Semantics',
		'HAS_RELATED': 'Related',
	}
