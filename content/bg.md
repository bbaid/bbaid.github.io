---
code: bg
label: BG
name: Български
---

<!--
The Bulgarian text of the site and the CV.

This file follows content/en.md section by section. Replace the English text
below with Bulgarian. Anything you leave out, or delete, falls back to English,
so the Bulgarian pages always build.

  # Heading {#id}      keep the {#id} exactly as it is; translate the heading.
  - `key`: value       keep the `key`; translate the value.
  - **Label** text     translate both parts.
  plain paragraphs     translate; keep the same number of paragraphs.

Images, links and categories are set in content/en.md and are not repeated here.
After editing, run:  python3 build.py   (it reports how much is still in English)
-->

# Site {#site}

- `title`: Bojan Baidanoff — GIS, cartography and spatial analysis
- `description`: Portfolio of Bojan Baidanoff, Geospatial Systems and Technologies student at Sofia University and founder of GIS Club SU: map atlases, climate and terrain posters, biodiversity web atlases and open-source spatial analysis.
- `share-description`: Map atlases, climate and terrain posters, biodiversity web atlases and open-source spatial analysis. Founder of GIS Club SU at Sofia University.
- `name`: Bojan Baidanoff
- `footer`: © 2026 Bojan Baidanoff · Боян Байданов
- `coordinates`: 42.6977° N, 23.3219° E

# Interface {#ui}

<!-- Short labels for buttons and screen readers. -->

- `skip`: Skip to content
- `home`: Bojan Baidanoff, back to top
- `sections`: Sections
- `language`: Language
- `theme`: Switch colour theme
- `view-map`: View map
- `filter`: Filter projects by theme
- `viewer`: Map viewer
- `viewer-close`: Close
- `viewer-previous`: Previous image
- `viewer-next`: Next image

# Bojan Baidanoff {#hero}

I make maps that answer a question — atlases, research posters and web maps built from open spatial data.

Third-year student of Geospatial Systems and Technologies at Sofia University “St. Kliment Ohridski”, and founder of [GIS Club SU](#club).

- `eyebrow`: 42°41′ N · 23°19′ E — Sofia, Bulgaria
- `button-work`: See the work
- `button-club`: GIS Club SU
- `button-cv`: CV
- `figure-label`: FIG. 01
- `figure-caption`: Green and blue infrastructure of Sofia’s functional urban area
- `image-alt`: Map of forest and grassland cores, green corridors and water bodies across the functional urban area of Sofia
- `caption`: Potential elements of green and blue infrastructure in the functional urban area of Sofia, 2026. Data: Copernicus Land Monitoring Service, Urban Atlas 2021, Street Tree Layer 2021.

## Facts {#facts}

- **36** map sheets in the V4+2 atlas, redrawn from open data
- **1,372** protected trees in my interactive map of Bulgaria’s register
- **310** Sofia neighbourhoods scored for walking access to services
- **15** founding members of GIS Club SU, which I chair

# Maps, posters and atlases {#work}

Recent projects from my studies and my own time. Select any map to see it full size.

- `nav`: Work
- `eyebrow`: Selected work

## V4+2 Map Atlas {#atlas}

A 36-sheet A3 atlas rebuilt for the *Common Spatial Development Strategy of the V4+2 Countries* — Czechia, Hungary, Poland, Slovakia, Bulgaria and Romania. It keeps the themes of the 2014 original, but every map is redrawn from the latest open data with one legend system, one typeface and one palette, so sheets can be compared at a glance.

The barriers chapter adds a conflict analysis of planned transport infrastructure against Natura 2000 sites and high mountains.

- `kicker`: Atlas · October 2026
- `method`: **How:** one Python script per sheet on a shared style library (layout, legend, basemap, labels, projections); output as vector PDF and 300 dpi PNG.
- `tags`: Python, GeoPandas, Rasterio, Matplotlib, OpenStreetMap, QGIS
- **36** sheets + cover
- **6** countries
- **~10 GB** source data

<!-- The labels around the book. The pages of the book itself are in templates/atlas-book.html. -->

- `book-label`: V4+2 Map Atlas, six selected sheets. Use the left and right arrow keys to turn pages.
- `book-first`: Cover
- `book-previous`: Previous page
- `book-next`: Next page
- `book-zoom`: View the sheets full size
- `book-overview`: All 36 sheets at a glance →
- `book-overview-caption`: All sheets of the V4+2 Map Atlas side by side: transport, technical infrastructure, population, economy, environment and barriers.
- `book-hint`: Click a page, swipe, or use the arrow keys to turn pages.

## Filters {#filters}

- `all`: All
- `nature`: Nature
- `climate`: Climate
- `terrain`: Terrain
- `people`: People and territory

## Projects {#projects}

### Bulgaria’s warming stripes {#stripes}

Ed Hawkins’ warming stripes, drawn separately for every Bulgarian province from 36 station records, 1961–2025. The last decade is 1.8 °C warmer than 1961–1990, and 2024 is the warmest year in the series. Where a station record has gaps, the value is estimated from neighbouring stations — and the poster says so.

- `kicker`: Climate · A3 poster
- `tags`: Python, Station data, Poster design
- `image-alt`: Dark poster of Bulgaria where each province is filled with blue-to-red climate stripes
- `caption`: Bulgaria’s warming stripes: one set of stripes per province, 1961–2025, with the records of 36 stations.

### Ridges and viewpoints {#ridges}

Multiply an elevation model by −1 and ridges become valleys, so flow accumulation traces ridgelines as if they were rivers. From those lines I pick prominent points and compute what each one sees within 10 km. The best viewpoint, Maragidik (1,814 m), sees 92 km²; the highest point (2,368 m) sees only 4.9 km². Prominence matters more than height.

- `kicker`: Terrain · Research poster
- `tags`: WhiteboxTools, gdal_viewshed, QGIS, Typst
- `image-alt`: Five-panel poster showing an inverted elevation model, flow accumulation, ridgelines and viewsheds
- `caption`: An inverted hydrological method for identifying mountain ridges, in five steps: inverted DEM, flow accumulation, ridgelines, viewpoint selection and visibility.

### Kyustendil Species Atlas {#kyustendil}

I read the distribution maps from the Red Data Book of Bulgaria and from the reference book on invasive plants onto the UTM 10 × 10 km grid, then joined them to the municipal boundary and the Natura 2000 sites. Each square shows how many taxa it holds; select one to list the species. Built with AI assistance.

- `kicker`: Biodiversity · Interactive web atlas
- `image-alt`: Dark web interface with a map of Kyustendil municipality, protected sites and a 10 km grid
- `caption`: Kyustendil Species Atlas: Natura 2000 sites over the UTM 10 × 10 km grid, with each site’s overlap with the municipality.
- **185** Red Book taxa
- **23** invasive plants
- **7** Natura 2000 sites
- `more`: Second view: species list →
- `more-caption`: Kyustendil Species Atlas: selecting a grid square lists its invasive plants with photos and field notes.

### Green and blue infrastructure of Sofia {#gbi}

Potential elements of green and blue infrastructure across Sofia’s functional urban area: forest and grassland cores, green and blue corridors, and the “stepping stones” that let species move through the city. An inset shows tree cover in the centre at street scale.

- `kicker`: Nature · Map
- `tags`: QGIS, Urban Atlas 2021, Street Tree Layer
- `image-alt`: Map of forest cores, grassland cores, corridors and water bodies around Sofia, with an inset of the city centre
- `caption`: Potential elements of green and blue infrastructure in the functional urban area of Sofia, 2026. Data: Copernicus Land Monitoring Service, Urban Atlas 2021, Street Tree Layer 2021.

### Forests of Burgas province {#burgas}

Broadleaf, coniferous and mixed forest from CORINE Land Cover 2018. Forest covers about 40 % of the province and is concentrated in Strandzha, in the south.

- `kicker`: Nature · Map
- `tags`: QGIS, CORINE 2018
- `image-alt`: Map of Burgas province with forest cover in shades of green, densest in the south
- `caption`: Where are the forests of Burgas province concentrated? Broadleaf, coniferous and mixed forest from CORINE Land Cover 2018.

### One party, two different maps {#elections}

A research poster from coursework in electoral geography. The question is methodological: does a party’s vote map in April predict where the presidential candidate it endorsed is strong in October? Across 265 municipalities the correlation is −0.16, and 0.02 once the municipalities led by one regional party are set aside — no relationship. The poster also states its limit: the data describe territories, not individual voters.

- `kicker`: Electoral geography · A0 poster
- `tags`: Spatial statistics, Typst, Claude Code
- `image-alt`: Research poster with two choropleth maps of Bulgaria by municipality, a turnout chart and a scatter plot
- `caption`: “One party, two different maps” — A0 research poster on the electoral geography of Bulgaria’s 2026 elections across 265 municipalities.

### Where do people live in Sofia? {#population}

Population density from address-level data of the National Statistical Institute, smoothed with kernel density estimation — the same technique as a heatmap of species records.

- `kicker`: People · Map
- `tags`: QGIS, Kernel density, NSI data
- `image-alt`: Dark map of Sofia with population density glowing from purple to orange
- `caption`: Where do people live in Sofia? Population density from address-level NSI data, smoothed with kernel density estimation.

### Land use in Stolichna municipality {#landuse}

The physical blocks of the municipality classified by land use, paired with a chart of each class’s share of the territory.

- `kicker`: Territory · Map and chart
- `tags`: QGIS, Land parcel data
- `image-alt`: Land-use map of Stolichna municipality next to a bar chart of land-use shares
- `caption`: Physical blocks in Stolichna municipality by land use, with a chart of each class’s share.

### Parcel staking plan {#staking}

Geodesy coursework: a staking plan for three parcels at 1:1000 in the Bulgarian coordinate system BGS2005, with the coordinates of every point tabulated.

- `kicker`: Geodesy · Plan
- `tags`: Surveying, BGS2005, 1:1000
- `image-alt`: Black and white survey plan of three parcels with a table of point coordinates
- `caption`: Staking plan for three parcels at 1:1000 in the Bulgarian coordinate system BGS2005, with the coordinate table of every point.

### Climate zones and world temperature {#climate}

A teaching poster of Alisov’s climate zones that ties each zone to climatograms of real stations — temperature and precipitation by month. Its companion sheet maps mean January and July air temperature from WorldClim 2.1, 1970–2000.

- `kicker`: Climate · A1 poster and maps
- `image-alt`: World map of climate zones in warm and cool bands, surrounded by small station climatograms
- `caption`: Climate zones after Alisov’s classification, with climatograms of stations around the world (A1 poster).
- `more`: Second sheet: January and July →
- `more-caption`: Mean monthly air temperature in January and July, 1970–2000. Source: WorldClim 2.1.

## Earlier maps {#earlier}

- `period`: 2025 – early 2026

### Fitness accessibility index {#gym}

- `note`: Sofia · hex grid, weighted index
- `image-alt`: Hexagonal grid map of Sofia in purple and orange showing the need for gyms
- `caption`: Where are gyms needed in Sofia? A weighted index on a hexagonal grid: population density (0.7) and distance to the nearest gym (0.3). Data: Meta population, OpenStreetMap.

### GDP per capita in Europe {#gdp}

- `note`: Eurostat · choropleth
- `image-alt`: Choropleth map of Europe by GDP per capita
- `caption`: GDP per capita across Europe, from Eurostat data.

### Rental market, Gresham, Oregon {#gresham}

- `note`: Demographics · density mapping
- `image-alt`: Map of Gresham, Oregon showing rental unit density
- `caption`: Rental unit density against age demographics in Gresham, Oregon.

### NYC pedestrian flows {#nyc}

- `note`: NYC Open Data · density
- `image-alt`: Vertical map of Manhattan with pedestrian flow highlighted
- `caption`: High-traffic pedestrian corridors in New York City, from NYC Open Data.

### NDVI, the Netherlands {#ndvi}

- `note`: Sentinel-2 · raster analysis
- `image-alt`: Satellite-derived vegetation index map of the Netherlands
- `caption`: NDVI from Sentinel-2 imagery over the Netherlands.

# GIS Club SU {#club}

In October 2026 I founded a student club at Sofia University for everyone who likes maps, data and satellites. I serve as its chair.

- `nav`: GIS Club SU
- `eyebrow`: Community
- `second-name`: ГИС клуб СУ

## Story {#club-story}

The founding general assembly on 9 October 2026 adopted the club’s statute and elected me chair. Fifteen students signed the founding protocol. The statute sets out how the club runs — a general assembly, a managing board and a chair elected each academic year — so that every next generation can pick up where the last one stopped.

Membership is free and open to students, lecturers, PhD students and anyone interested in GIS and remote sensing. ArcGIS or QGIS, everyone is welcome.

- `note`: I also designed the club’s visual identity: a Swiss-style system in navy and stepped blues, built around contour bands and a point-cloud image of the university’s Rectorate.

## What the club is for {#club-goals}

- **Make geospatial technology visible** to students and to the public.
- **Build an informal community** where students and lecturers share knowledge and ideas.
- **Support members’ growth**, academic and professional.
- **Connect the university with industry** in geospatial technology.

## How {#club-how}

Public lectures, seminars and workshops · guest speakers from academia and industry · hackathons and map challenges · field trips · partnerships with departments and organisations.

## Timeline {#club-timeline}

### Founding general assembly {#club-founding}

- `when`: 9 October 2026
- `detail`: Statute adopted · chair elected

### First seminar: Introduction to GIS {#club-seminar}

- `when`: 11 November 2026
- `detail`: Hands-on with QGIS, using a worksheet I prepared · Room 287, north wing of the Rectorate

### Lectures, workshops, hackathons {#club-next}

- `when`: Next
- `detail`: Map challenges, field trips and meetings with specialists from the university and industry

## Announcement {#club-post}

- `image-alt`: Navy announcement poster in Bulgarian for the club’s first seminar, with contour lines and the club emblem
- `caption`: Announcement for the first seminar of GIS Club SU, 11 November 2026: “Introduction to GIS — we’ll work with real GIS software (QGIS)”.
- `note`: Announcement for the first seminar, in the club’s visual identity
- `emblem-alt`: Club emblem: the Rectorate of Sofia University rendered as a coloured point cloud

# Open-source projects {#code}

Reproducible analyses and interactive maps on [GitHub](https://github.com/bbaid).

- `nav`: Code
- `eyebrow`: Code and web maps
- `label-map`: Interactive map
- `label-code`: Code
- `label-team`: team project

## Sofia — access to basic services {#repo-services}

How well Sofia’s 310 neighbourhoods are served by hospitals, schools, kindergartens, police, supermarkets and pharmacies. OpenStreetMap facilities meet the Census 2021 population grid on a pedestrian network: nearest-service walking distance, 10-minute coverage, a composite access index and LISA hotspots.

- `tags`: Python, OSMnx, GeoPandas, PySAL, Mapbox GL JS

## Venerable trees of Bulgaria {#repo-trees}

A bilingual interactive map of 1,372 protected centuries-old trees from the national register, grouped by species, with age, height and girth for each tree. A small Python script converts the register spreadsheet to GeoJSON.

- `tags`: Mapbox GL JS, Python, GeoJSON, GitHub Actions

## China’s niche industry towns {#repo-china}

A map of 61 Chinese towns and counties that make a large share of one product — buttons in Qiaotou, oil paintings in Dafen. Every coordinate is checked against OpenStreetMap, and the README is frank about which market-share claims are only “reported”.

- `tags`: Leaflet, Python, Nominatim, GitHub Actions

## The average colour of every country {#repo-colour}

The mean Sentinel-2 satellite colour of each country and of Bulgaria’s regions, provinces and municipalities, written back into the shapefile. A pure-Python re-creation of Erin Davis’s project: download, mask to the border, average with a latitude weight — no GDAL required.

- `tags`: Python, Sentinel-2 cloudless, Pillow, WMS

## Dogs of Sofia {#repo-dogs}

A pipeline that downloads and cleans Sofia’s dog registry and the Call Sofia complaint signals, aggregates them by district and publishes a web map with district shading and complaint points.

- `tags`: Python, GeoPandas, Web scraping, Mapbox GL JS

## NeroSense — adaptive water intelligence {#repo-nerosense}

Our team’s entry for the 11th CASSINI Hackathon. Satellite indicators of chlorophyll, turbidity and temperature are turned into priority maps that tell an autonomous surface robot where to sample — tested on phytoplankton blooms in the Iskar reservoir.

- `tags`: Sentinel-2/3, Google Earth Engine, FastAPI, PostgreSQL

# Background and toolbox {#about}

I study how places work and how to show it clearly. Most of my projects start with a question — where is something missing, what changed, what can be seen from here — and end as a map someone else can read without me in the room.

I work across the whole chain: finding and cleaning open data, analysis in Python and QGIS, and the layout of the final sheet. I’m most interested in GIS and remote sensing for research, and in teaching them — which is why I started GIS Club SU and prepare introductory QGIS lessons.

- `nav`: About
- `eyebrow`: About
- `languages`: **Languages:** Bulgarian (native) · English (C2 — Cambridge English: Advanced, 2025)

## Education and experience {#about-path}

- **2023 – now** **Sofia University “St. Kliment Ohridski”** — BSc Geospatial Systems and Technologies, Faculty of Geology and Geography. Grade average 5.95 / 6.00. Three Erasmus+ exchanges.
- **2026 – now** **GIS Club SU** — founder and chair.
- **2026** **CASSINI Hackathon**, 11th edition — team NeroSense.
- **2020 – 2023** **Uni4kids** — intern, science communicator.
- **2018 – 2023** **National High School of Mathematics and Natural Sciences** “Acad. Lyubomir Chakalov”, Sofia.

## Toolbox {#toolbox}

- **GIS** QGIS · ArcGIS Pro · ArcGIS Online · StoryMaps
- **Code and data** Python (GeoPandas, Rasterio, Pandas, Matplotlib, OSMnx) · GDAL · WhiteboxTools · SQL and PostGIS
- **Remote sensing** Sentinel-2 · CORINE and Copernicus layers · DEM analysis, viewsheds, NDVI
- **Web maps** Mapbox GL JS · Leaflet · GitHub Pages and Actions
- **Layout** QGIS layouts · Typst · Affinity

## How I work with AI {#ai}

- **I set the question and the method.** AI carries out steps; it doesn’t decide what I study.
- **I check every result** against the source data before it reaches the map.
- **I say openly what AI did** — on the map itself, next to the data sources.

# Have a question a map could answer? {#contact}

I’m open to internships, research collaborations and guest talks for GIS Club SU.

- `nav`: Contact
- `eyebrow`: Contact
- `label-linkedin`: LinkedIn
- `label-github`: GitHub
- `label-cv`: CV
- `label-cv-pdf`: CV (PDF)

# Боян Байданов {#cv}

<!-- The CV is one A4 page. Keep the text short enough to fit: `python3 build.py --pdf` warns if it runs over. -->

- `title`: Боян Байданов — автобиография
- `description`: Автобиография на Боян Байданов: ГИС, картография и пространствен анализ. Студент по „Геопространствени системи и технологии“ в Софийския университет, основател на ГИС клуб СУ.
- `eyebrow`: 42°41′ N · 23°19′ E — София, България
- `role`: ГИС, картография и пространствен анализ
- `photo-alt`: Портрет на Боян Байданов
- `back`: ← Портфолио
- `download`: Изтегли PDF
- `options`: Настройки на автобиографията
- `footer`: Боян Байданов · автобиография · ноември 2026&nbsp;г.
- `pdf`: CV_Bojan_GIS_BG.pdf
- `compact`: yes

## Профил {#cv-profile}

Студент в трети курс по „Геопространствени системи и технологии“ в Софийския университет. Превръщам отворени пространствени данни в атласи, научни постери и уеб карти. Основател и председател на ГИС клуб СУ. Търся стаж в областта на ГИС и дистанционните изследвания.

## Избрани проекти {#cv-projects}

- `more`: Всички проекти, с картите: [bbaid.github.io](https://bbaid.github.io/)

### Атлас V4+2 {#cv-atlas}

Атлас от 36 листа във формат А3 към стратегията за пространствено развитие на шест държави от Централна и Източна Европа, изчертан наново с актуални отворени данни. По един скрипт на лист върху обща стилова библиотека.

- `year`: 2026
- `tools`: Python · GeoPandas · Rasterio · Matplotlib

### София – достъп до основни услуги {#cv-services}

Пешеходен достъп до шест вида услуги за 310 квартала: обекти от OpenStreetMap и преброителната мрежа на населението върху пешеходна мрежа, съставен индекс и LISA клъстери.

- `year`: 2026
- `tools`: Python · OSMnx · PySAL · Mapbox GL JS

### Била и панорамни площадки {#cv-ridges}

Метод с обърнат цифров модел на релефа: натрупването на оттока очертава билата, а площадките се подреждат по видимата площ до 10&nbsp;km.

- `year`: 2026
- `tools`: WhiteboxTools · GDAL · QGIS · Typst

### Затоплянето в България {#cv-stripes}

Климатични ивици за всяка област, 1961–2025&nbsp;г., по записите на 36 станции; оценките за липсващите данни са отбелязани на постера.

- `year`: 2026
- `tools`: Python

### Атлас на видовете в община Кюстендил {#cv-kyustendil}

Интерактивен атлас на 185 таксона от Червената книга и 23 инвазивни растения по мрежата UTM 10&nbsp;×&nbsp;10&nbsp;km, свързан със седем зони от Натура 2000.

- `year`: 2026

### Вековните дървета на България {#cv-trees}

Двуезична интерактивна карта на 1372 защитени вековни дървета от националния регистър.

- `year`: 2026
- `tools`: Mapbox GL JS · Python

## Опит и инициативи {#cv-experience}

### ГИС клуб СУ, Софийски университет {#cv-club}

Основах студентския клуб с 15 учредители и писмен устав; организирах първия семинар – въведение в ГИС с QGIS; създадох визуалната му идентичност.

- `when`: от 10.2026
- `role`: основател и председател

### Хакатон CASSINI, 11-о издание {#cv-cassini}

Спътникови показатели насочват надводен робот къде да взема водни проби.

- `when`: 2026
- `role`: отбор NeroSense

### Uni4kids {#cv-uni4kids}

- `when`: 2020 – 2023
- `role`: стажант, комуникатор на науката

## Образование {#cv-education}

### Софийски университет „Св. Климент Охридски“ {#cv-su}

Бакалавър, „Геопространствени системи и технологии“, Геолого-географски факултет. Среден успех 5,95 / 6,00. Три обмена по програма „Еразъм+“.

- `when`: 2023 – сега

### Национална природо-математическа гимназия „Акад. Любомир Чакалов“ {#cv-npmg}

Профил „Икономическо развитие“. Среден успех 5,84 / 6,00.

- `when`: 2018 – 2023

## Инструменти {#cv-toolbox}

- **ГИС** QGIS · ArcGIS Pro · ArcGIS Online · StoryMaps
- **Код и данни** Python (GeoPandas, Rasterio, Pandas, Matplotlib, OSMnx) · GDAL · WhiteboxTools · SQL и PostGIS
- **Дистанционни изследвания** Sentinel-2 · CORINE и слоеве на Copernicus · анализ на ЦМР, видимост, NDVI
- **Уеб карти** Mapbox GL JS · Leaflet · GitHub Pages
- **Оформление и отчети** QGIS · Typst · Affinity · Excel · Tableau · Power BI

## Езици {#cv-languages}

- **Български** — роден
- **Английски** — C2. Cambridge English: Advanced, 202 точки (2025&nbsp;г.)

## Отличия и доброволчество {#cv-awards}

- **Най-добър стартъп проект** — Institute for Social and Economic Engineering, 2025&nbsp;г.
- **Софийски фестивал на науката** — доброволец, 2024&nbsp;г.

## Интереси {#cv-interests}

Планинарство · колоездене · настолни игри · видеоигри
