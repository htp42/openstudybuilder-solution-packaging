const categoryActivityItemClasses = {
  CategoricFindings: 'finding_category',
  NumericFindings: 'finding_category',
  TextualFindings: 'finding_category',
  Events: 'event_category',
  Interventions: 'intervention_category',
}

const subcategoryActivityItemClasses = {
  CategoricFindings: 'finding_subcategory',
  NumericFindings: 'finding_subcategory',
  TextualFindings: 'finding_subcategory',
  Events: 'event_subcategory',
  Interventions: 'intervention_subcategory',
}

const sdtmDomainAbbreviationCodelistUid = 'C66734'

export default {
  categoryActivityItemClasses,
  subcategoryActivityItemClasses,
  sdtmDomainAbbreviationCodelistUid,
}
