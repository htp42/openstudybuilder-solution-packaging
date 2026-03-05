import repository from '../repository'

const resource = 'ct/codelists'

export default {
  getAll(params) {
    return repository.get(`${resource}`, { params })
  },
  getCodelistTerms(codelistUid, params) {
    return repository.get(`${resource}/${codelistUid}/terms`, { params })
  },
  search(params) {
    return repository.get(`${resource}/full-text-search`, { params })
  },
  searchByTerm(params) {
    return repository.get(`${resource}/full-text-search-by-term`, { params })
  },
}
