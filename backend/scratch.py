from pathlib import Path

fp = Path(r'd:\Softwarica\IR\CW\frontend\src\components\search\PublicationResultCard.tsx')
content = fp.read_text(encoding='utf-8')

old_doi = '''            {result.doi && (
              <span
                className="inline-flex max-w-full items-center gap-1.5 truncate text-xs font-medium text-[var(--text-faint)]"
                title={DOI: }
              >
                <Fingerprint size={13} />
                DOI {result.doi}
              </span>
            )}'''

new_doi = '''            {result.doi && (
              <a
                href={https://doi.org/}
                target="_blank"
                rel="noreferrer"
                className="inline-flex max-w-full items-center gap-1.5 truncate text-xs font-medium text-[var(--text-faint)] transition hover:text-[var(--accent)]"
                title={View on DOI.org: }
              >
                <Fingerprint size={13} />
                DOI {result.doi}
              </a>
            )}'''

content = content.replace(old_doi, new_doi)

old_year = '''                    <span className="inline-flex items-center gap-1 text-[var(--text-faint)]">
                      <CalendarDays size={12} />
                      {result.year}
                    </span>'''

new_year = '''                    <span className="inline-flex items-center gap-1 text-[var(--text-faint)]" title="Publication Date">
                      <CalendarDays size={12} />
                      Published: {result.year}
                    </span>'''

content = content.replace(old_year, new_year)
fp.write_text(content, encoding='utf-8')
