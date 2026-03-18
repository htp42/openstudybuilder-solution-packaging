/**
 * Extract field paths and human-readable labels from an OpenAPI specification.
 */

import fs from 'node:fs'
import path from 'node:path'
import readline from 'node:readline'

const ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
const DEFAULT_OPENAPI_PATH = 'clinical-mdr-api/openapi.json'
const OUTPUT_PATH = 'output.txt'

/**
 * Title-case a field name matching Python's str.title() behavior,
 * then replace underscores with spaces and fix "Uid" → "UID".
 *
 * Python's title(): uppercase char after non-alphanumeric boundary,
 * lowercase all other alpha chars.
 * @param {string} name
 * @returns {string}
 */
function titleize(name) {
  let result = ''
  let prevIsAlnum = false
  for (const ch of name) {
    const isAlpha = /[a-zA-Z]/.test(ch)
    if (isAlpha) {
      result += prevIsAlnum ? ch.toLowerCase() : ch.toUpperCase()
    } else {
      result += ch
    }
    prevIsAlnum = isAlpha
  }
  return result.replaceAll('_', ' ').replaceAll('Uid', 'UID')
}

/**
 * Convert a comma-separated field path into a human-readable label.
 *
 * Examples:
 *   "name"                  -> "Name"
 *   "actions,a,action"      -> "Action of Actions #{a}"
 *   "actions,a,field,b,uid" -> "UID of Field #{b} of Actions #{a}"
 *
 * @param {string} key
 * @returns {string}
 */
function buildLabel(key) {
  const parts = key.split(',').reverse()

  if (parts.length === 1) {
    return titleize(parts[0]).trim()
  }

  let label = ''
  let prevWasIndex = false

  for (let idx = 0; idx < parts.length; idx++) {
    const part = parts[idx]

    if (ALPHABET.includes(part) && part.length === 1) {
      prevWasIndex = true
      continue
    }

    const title = titleize(part)
    if (prevWasIndex) {
      label += `${title} #{${parts[idx - 1]}} of `
    } else {
      label += `${title} of `
    }
    prevWasIndex = false
  }

  label = label.trim()
  if (label.endsWith('of')) {
    label = label.slice(0, -2).trim()
  }
  return label
}

/**
 * Find a $ref in a schema property, handling items and anyOf wrappers.
 * @param {Object} schema
 * @returns {string|null}
 */
function findNestedRef(schema) {
  if (schema.items && schema.items['$ref']) {
    return schema.items['$ref']
  }

  if (schema['$ref']) {
    return schema['$ref']
  }

  if (schema.anyOf) {
    for (const item of schema.anyOf) {
      if (item.items && item.items['$ref']) {
        return item.items['$ref']
      }
    }
    for (const item of schema.anyOf) {
      if (item['$ref']) {
        return item['$ref']
      }
    }
  }

  return null
}

/**
 * Recursively extract body field paths from an OpenAPI schema reference.
 * @param {Object} schemas
 * @param {string} ref
 * @param {string} suffix
 * @param {number} depth
 * @returns {string[]}
 */
function extractBodyFields(schemas, ref, suffix = '', depth = -1) {
  const results = []
  const schemaName = ref.split('/').pop()
  const properties = (schemas[schemaName] || {}).properties || {}

  for (const [fieldName, fieldSchema] of Object.entries(properties)) {
    const indexPrefix = depth > -1 ? `${ALPHABET[depth]},` : ''
    const currentPath = `${suffix}${indexPrefix}${fieldName},`

    const nestedRef = findNestedRef(fieldSchema)
    if (nestedRef) {
      results.push(
        ...extractBodyFields(schemas, nestedRef, currentPath, depth + 1)
      )
    }

    const key = currentPath.replace(/,$/, '')
    const label = buildLabel(key)
    results.push(`"body,${key}": "${label}",`)
  }

  return results
}

/**
 * Extract a $ref from a response/request JSON content block.
 * @param {Object} content
 * @returns {string}
 */
function extractRefFromContent(content) {
  const jsonSchema = ((content || {})['application/json'] || {}).schema || {}
  return jsonSchema['$ref'] || (jsonSchema.items || {})['$ref'] || ''
}

/**
 * Extract all parameter and body field entries from an OpenAPI spec.
 * @param {Object} data
 * @returns {string[]}
 */
function extractFields(data) {
  const results = []
  const schemas = data.components.schemas

  for (const pathObj of Object.values(data.paths)) {
    for (const operation of Object.values(pathObj)) {
      if (operation.parameters) {
        for (const param of operation.parameters) {
          const name = param.name.replace(/\[\]$/, '')
          const location = param.in
          results.push(
            `"${location},${name},a": "${name} #{a} in ${location} parameters",`
          )
        }

        const bodyRef =
          ((
            ((operation.requestBody || {}).content || {})['application/json'] ||
            {}
          ).schema || {})['$ref'] || ''
        if (bodyRef) {
          results.push(...extractBodyFields(schemas, bodyRef))
        }
      }

      for (const response of Object.values(operation.responses || {})) {
        const bodyRef = extractRefFromContent(response.content)
        if (bodyRef) {
          results.push(...extractBodyFields(schemas, bodyRef))
        }
      }
    }
  }

  return results
}

/**
 * Prompt the user for input via stdin.
 * @param {string} prompt
 * @returns {Promise<string>}
 */
function ask(prompt) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  })
  return new Promise((resolve) => {
    rl.question(prompt, (answer) => {
      rl.close()
      resolve(answer)
    })
  })
}

const openApiPath =
  (await ask(
    'Provide the absolute path to the OpenAPI JSON file (e.g., /path/to/openapi.json): '
  )) || DEFAULT_OPENAPI_PATH

const raw = fs.readFileSync(path.resolve(openApiPath), 'utf-8')
const data = JSON.parse(raw)
const results = extractFields(data)

const unique = [...new Set(results)].sort()
fs.writeFileSync(OUTPUT_PATH, unique.join('\n'), 'utf-8')
