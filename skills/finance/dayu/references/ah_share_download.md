# A-Share And Hong Kong Download Guide

Use this reference when the target company is listed in Hong Kong or mainland China and the relevant filing PDFs are not already available locally.

This reference is for closing the loop before Dayu upload:

1. identify the market
2. download the report PDF from an official source
3. upload it into Dayu
4. continue with `prompt` or `interactive`

## Principle

For A-share and Hong Kong names, prefer official disclosure sources first:

- Hong Kong: HKEXnews, then company investor relations site
- A-share: the relevant exchange disclosure page first, then CNINFO or company investor relations site

Do not default to random mirrors, reposted PDFs, or broker-hosted copies when an official source is available.

## Minimum useful set

If the user only wants enough material to start research, see the minimum-material guidance in [materials.md](materials.md). This download guide focuses only on finding the official files.

## Hong Kong workflow

### Source priority

- HKEXnews title search: [HKEXnews title search](https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=EN)
- HKEXnews predefined annual reports: [HKEXnews annual reports](https://www1.hkexnews.hk/search/predefineddoc.xhtml?predefineddocuments=3)
- company IR page when available

### Minimal steps

1. Search by stock code or company name on HKEXnews.
2. Filter for `Annual Report`, `Interim Report`, or related financial statements.
3. Open the PDF from HKEXnews.
4. If HKEX search is awkward, use the company IR financial reports page as a fallback.
5. Download the PDF locally.

### Agent guidance

An agent can:

- search the official HKEXnews title search page
- use the company IR page when it directly exposes report PDFs
- download the PDF to a local temp path
- then run Dayu upload commands

### Verified example: Tencent 2025 annual report

Tencent's 2025 annual report is available from official Tencent investor relations pages:

- investor reports landing page: [Tencent financial reports](https://www.tencent.com/en-us/investors/financial-reports.html)
- direct PDF: [Tencent 2025 Annual Report PDF](https://static.www.tencent.com/uploads/2026/04/09/62d786fcf3d3c8cb7e54791ee95439ac.pdf)

It also appears in HKEXnews title search results for stock code `00700` under `Annual Report 2025`.

### Verified example: Xiaomi 2025 fiscal-year fallback

Xiaomi is a useful Hong Kong fallback example because its official IR site already exposes `2025` full-year results materials even when the `Annual Report` page does not yet list a `2025 Annual Report` PDF.

Official Xiaomi sources:

- investor relations homepage: [Xiaomi IR](https://ir.mi.com/)
- annual and interim reports page: [Xiaomi Annual & Interim Reports](https://ir.mi.com/financial-information/annual-interim-reports/)
- quarterly results page: [Xiaomi Quarterly Results](https://ir.mi.com/financial-information/quarterly-results/)
- 2025 annual results announcement event page: [Xiaomi 2025 Annual Results Announcement](https://ir.mi.com/events/event-details/xiaomi-corporation-2025-annual-results-announcement)

What this shows:

- the `Annual & Interim Reports` page currently lists `2025 Interim Report`, but not a `2025 Annual Report` entry
- the IR homepage and event pages already expose `2025 Annual Results Announcement`
- the `Quarterly Results` section includes `2025 Q4 Results Announcement` and `2025 Q4 Results Presentation`

Practical interpretation:

- if the user wants to study `2025` full-year performance, the official `Annual Results Announcement` and `Q4 Results` materials are already usable
- if the user explicitly wants the complete `Annual Report` PDF, first check the annual reports page and HKEXnews; if it is still missing, tell the user the full-year results materials are available now and the complete annual report may be published later

Use Xiaomi as the model case for this fallback rule:

1. first check whether the official `Annual Report` PDF exists
2. if it does not, use the official `Annual Results Announcement`
3. add `Q4 Results Presentation`
4. add the latest `Interim Report` if deeper context is needed

## A-share workflow

### Source priority

- Shanghai Stock Exchange: [SSE](https://www.sse.com.cn/)
- SSE STAR Market company page example: [SMIC on SSE STAR Market](https://www.sse.com.cn/star/en/marketdata/snapshot/c/5481443.shtml)
- Shenzhen Stock Exchange: [SZSE](https://www.szse.cn/)
- CNINFO homepage: [CNINFO](https://www.cninfo.com.cn/)
- CNINFO disclosure search entry: [CNINFO search](https://www.cninfo.com.cn/new/commonUrl/pageOfSearch?lastPage=index&url=disclosure%2Flist%2Fsearch)
- company IR page when available

Use the exchange site that matches the listing venue whenever possible. CNINFO is still useful as a practical unified search surface, but it should not be treated as the only official route for every A-share case.

### Exchange-first routing

#### SSE / STAR Market prefixes

Prefer:

- SSE disclosure pages
- STAR Market company disclosure pages
- then company IR
- then CNINFO as a fallback search surface

This is the right default for companies with prefixes such as `600`, `601`, `603`, `605`, and `688`.

#### SZSE prefixes

Prefer:

- SZSE disclosure pages
- then company IR
- then CNINFO

This is the right default for companies with prefixes such as `000`, `001`, `002`, `003`, and `300`.

### Minimal steps

1. Identify whether the company is on SSE, STAR Market, SZSE, or another mainland venue.
2. Search by stock code or company name on the matching exchange site first, then use CNINFO if needed.
3. Locate the latest annual report, interim report, or quarterly report.
4. Open the official PDF.
5. Download it locally.

### Agent guidance

An agent should prefer browser-style navigation over undocumented scraping:

- open the matching exchange disclosure page first when the listing venue is known
- otherwise use CNINFO to search by code or company name
- search by code or company name
- identify the annual report or interim report title
- open the official PDF
- download the PDF locally

If exchange navigation or CNINFO is hard to automate in a given environment, fall back to the company's own IR page rather than an unofficial mirror.

### Verified example: SMIC A-share annual report workflow

SMIC is a useful A-share example because its STAR Market code is `688981`, and its official company financial reports page exposes report PDFs directly.

Verified official source:

- company financial reports page: [SMIC financials](https://www.smics.com/en/site/company_financialSummary)
- SSE STAR Market annual report PDF: [SMIC 2024 annual report on SSE](https://star.sse.com.cn/disclosure/listedinfo/announcement/c/new/2025-03-28/688981_20250328_JLBJ.pdf)
- direct PDF confirmed from the official SMIC site: [SMIC 688981 annual report PDF](https://www.smics.com/uploads/67f640fd/688981.pdf)

### A-share manual example steps

1. Open the SSE STAR Market company disclosure page, the official company reports page, or CNINFO.
2. Search `688981` or `中芯国际`.
3. Look for the annual report entry and confirm its fiscal year in the title.
4. Open the official PDF.
5. Download it locally.
6. Upload it to Dayu with the correct fiscal metadata.

## After download

Once the PDF is local, switch to [materials.md](materials.md) for upload commands, required metadata, and the return path back into `prompt`.

## If the PDF upload fails

For Hong Kong and A-share filings, an official PDF may still fail during Dayu conversion. In that case, follow the PDF-to-Markdown fallback in [materials.md](materials.md) rather than repeating the same upload path here.

Xiaomi is a concrete example of this pattern:

- official HKEX PDF download was fine
- direct PDF upload hit conversion trouble
- Markdown converted from the same official PDF uploaded successfully and unblocked Dayu analysis

## Common pitfalls

- Hong Kong reports often publish in the following calendar year. For example, a `2025 annual report` may be published in 2026.
- Some Hong Kong issuers publish full-year results announcements before the complete annual report PDF is available. Xiaomi is a concrete example of this pattern.
- A-share and Hong Kong naming is not perfectly uniform; search by stock code whenever possible.
- Prefer the full annual report PDF over a summary announcement when the user wants deep research.
- If the user only has a results announcement but not the annual report yet, upload it anyway and note the limitation.
