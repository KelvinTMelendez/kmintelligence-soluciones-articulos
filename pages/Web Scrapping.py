#Importar Librerias
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Web scraping", layout="wide")
IMG_DIR = Path(__file__).resolve().parent

# ========== ÍNDICE (SIDEBAR) ==========
st.sidebar.title("Índice")
st.sidebar.markdown("""
- [Introducción](#introduccion)
- [Cómo funciona](#como-funciona)
- [Tipos de web scraping](#tipos-de-web-scraping)
  - [Manual](#manual)
  - [Automatizado](#automatizado)
  - [Con navegadores](#con-navegadores)
  - [Con API](#con-api)
- [Marco legal](#marco-legal-del-web-scraping)
  - [Cómo saber si está prohibido o no](#como-saber-si-esta-prohibido-o-no)
  - [Términos de Servicio](#terminos-de-servicio)
  - [Barrera técnica](#barrera-tecnica)
  - [robots.txt](#robotstxt)
  - [Infraestructura](#infraestructura)
- [Buenas prácticas y checklist ético](#buenas-practicas-y-checklist-etico)
  - [Checklist pre-scraping](#checklist-pre-scraping)
  - [Checklist durante el scraping](#checklist-durante-el-scraping)
- [Precedentes](#precedentes-casos-legales)
  - [hiQ Labs v. LinkedIn](#hi-q-labs-v-linked-in)
  - [Facebook v. Power Ventures](#facebook-v-power-ventures)
  - [Ryanair v. Atrápalo y PR Aviation](#ryanair-v-atrápalo-y-pr-aviation)
- [Conclusiones](#conclusiones)
""")

# ========== CONTENIDO ==========

st.title("Web scraping sin líos: qué es legal, qué no y cómo hacerlo bien")
st.markdown("""
## Introducción
El _web scraping_ es una técnica que te permite extraer información de manera automática de páginas web mediante un _script_ o programa que visita un sitio web, analiza la estructura HTML y toma datos de interés.Los científicos de datos utilizan estas técnicas para enriquecer sus estudios estadísticos con datos externos disponibles en la web.

## Cómo funciona
En esencia, el web scraping consiste en 4 pasos:

1.  **Acceso a la página web objetivo**: El _script_ o programa visita la página web para extraer su estructura HTML.
2.  **Lectura del HTML**: El _script_ analiza el HTML descargado.
3.  **Extracción**: Se localizan los elementos HTML específicos que contienen la información de interés.
4.  **Procesamiento**: Los datos se limpian y organizan en estructuras tabulares como Excel, CSV o TXT.

## Tipos de web scraping

### Manual
En esencia, es el acto humano de copiar y pegar los datos de interés de una página web a una estructura tabular (ya sea Excel, CSV y demás).

### Automatizado
Aquí, el técnico desarrolla _scripts_ que automáticamente:

1.  Acceden a la página web objetivo para extraer su estructura HTML.
2.  Leen el HTML descargado.
3.  Extraen la información de interés localizada en elementos HTML específicos.
4.  Procesan y organizan los datos en estructuras tabulares (Excel, CSV, TXT).

Algunas librerías utilizadas para el desarrollo de estos _scripts_ son:

-   requests
-   beautifulsoup4


### Con navegadores
Este tipo de scraping utiliza el navegador para simular acciones de un ser humano. Es ideal para sitios web donde el contenido se carga dinámicamente.

Algunas librerías utilizadas para el desarrollo de estos _scripts_ son:

-   Selenium
-   Playwright


### Con API
El enfoque es consumir las API disponibles en la web.


## Marco legal del web scraping
El web scraping (o raspado web) es una herramienta fundamental para la recolección masiva y automatizada de datos en la era digital. Sin embargo, su legalidad reside en una compleja zona gris, donde la permisibilidad está sujeta a la estricta observancia de los derechos contractuales, de propiedad intelectual y las regulaciones de privacidad. Contrariamente a la creencia popular, la simple accesibilidad pública de un dato no lo exime de protección legal.

La ley no prohíbe el web scraping de forma absoluta, sino que lo considera una actividad legalmente condicional. Todo dependerá de:

-   **El tipo de dato que se extraiga**: Si son datos personales de usuarios, obviamente, tiene un peso mayor que otros datos como la lotería.
    -   **Reglamento General de Protección de Datos (RGPD)**: Prohíbe el tratamiento de datos personales (incluyendo su recopilación masiva) sin contar con una base de legitimación válida (como el consentimiento o el interés legítimo debidamente justificado). Sanciona la falta de protección de datos personales, incluso si son de acceso público.

    -   **Ley de Privacidad del Consumidor de California (CCPA)**: Prohíbe la venta de datos personales de residentes de California sin ofrecerles un mecanismo visible y claro de exclusión voluntaria (_opt-out_), como el enlace "Do Not Sell My Personal Information".

-   **El método utilizado para extraer los datos**: Si tu tecnología atenta contra la permanencia de los servidores del proveedor, puede ser una variable en contra para el técnico dentro del marco legal, ya que estás atentando contra el modelo de negocio del proveedor.

    -   **Ley de Fraude y Abuso Informático (CFAA)**: Prohíbe el acceso a un sistema informático sin autorización o excediendo el acceso autorizado, lo que incluye romper barreras de autenticación (_logins_), usar cuentas falsas o acceder a áreas restringidas del servidor.

    -   **Trespass to Chattels**: Prohíbe la interferencia sustancial con la propiedad privada de otro. En el contexto digital, se invoca cuando el scraping masivo y excesivo causa un daño palpable al servidor, como la degradación del rendimiento o el consumo excesivo de ancho de banda.

-   **El propósito de los datos**: Si los datos recopilados se utilizan con fines didácticos, tendrá menos peso legal en términos de consecuencias que un uso mercantil o con fines de lucro.

    -   **Derecho Sui Generis de las Bases de Datos (Directiva 96/9/CE)**: Prohíbe la extracción y/o reutilización de una parte sustancial del contenido de una base de datos cuando su creador ha realizado una inversión sustancial in su obtención, verificación o presentación, incluso si los datos en sí son puramente fácticos.

El riesgo legal para los especialistas en datos persiste, incluso si los datos son visibles sin necesidad de iniciar sesión, y las posibles responsabilidades pueden abarcar el Derecho Penal/Cibernético, el Derecho Civil (incumplimiento contractual, interferencia), el Derecho de la Propiedad Intelectual y la violación de las leyes de Protección de Datos.

### ¿Cómo saber si está prohibido o no?

El técnico en datos debe tener en cuenta los siguientes puntos antes de realizar web scraping:

#### Términos de Servicio
¿Han visto que al momento de ingresar a un sitio web, al final de la página, en el _footer_, tienen un enlace que se llama "Terms of Use" (o "Términos de Uso")?

Este documento detalla las pautas que el proveedor estableció para el uso de su sitio web. Esto puede incluir cláusulas específicas sobre el web scraping o el acceso automatizado.

#### Barrera técnica

##### robots.txt
El técnico en datos debe considerar el archivo `robots.txt` que poseen los sitios web. Este archivo es un componente técnico que poseen los sitios web donde se documenta la barrera técnica y ética que debe cumplir un _scraper_ de datos.

El archivo documenta lo siguiente:

1.  Las URL o directorios a los que el bot tiene permiso para acceder.
2.  Las partes que puede revisar.

Un ejemplo de `robots.txt` sería:

```txt
User-agent: *
Disallow: /admin/
Disallow: /privado/
Allow: /
```

Explicación:

```txt
User-agent: * → Aplica a todos los bots.
Disallow: /admin/ → No deben acceder a la carpeta /admin/.
Allow: / → Todo lo demás está permitido.
```

Para acceder al archivo:
`https://tusitio.com/robots.txt`

##### Infraestructura

La ley prohíbe el scraping que cause un daño perceptible o una interferencia sustancial con el uso y rendimiento de la propiedad (el servidor). Si el _scraper_ envía un volumen excesivo de peticiones por segundo que degrada el servicio o consume ancho de banda, puede dar lugar a demandas civiles por interferencia con bienes muebles.


## Buenas Prácticas y Checklist Ético

Además de comprender el marco legal, seguir un conjunto de buenas prácticas es fundamental para realizar un web scraping ético y de bajo riesgo. Aquí tienes una lista de verificación para guiar tu trabajo.

#### Checklist Pre-Scraping
- [ ] **Leer los "Términos de Servicio" (ToS):** Es el contrato entre tú y el proveedor del sitio. Busca cláusulas que prohíban explícitamente el acceso automatizado o la reproducción de datos.
- [ ] **Revisar y respetar `robots.txt`:** Este archivo es la guía técnica que indica a qué partes del sitio no debes acceder con tu bot. Es la primera norma de cortesía en el mundo del scraping.
- [ ] **Evaluar el tipo de dato:** ¿Los datos son públicos, personales o sensibles? La extracción de datos personales está fuertemente regulada (RGPD, CCPA) y requiere una base legal sólida.
- [ ] **Buscar una API oficial:** Antes de scrapear, comprueba si el sitio web ofrece una API (Interfaz de Programación de Aplicaciones). Usar la API es siempre el método preferido, más seguro, estable y 100% legal.

#### Checklist Durante el Scraping
- [ ] **Identifica tu bot:** Configura un `User-Agent` descriptivo en las cabeceras de tus peticiones. Esto le permite al administrador del sitio saber quién está accediendo a sus recursos (ej. `User-Agent: MiBotDeScrapingAcademico/1.0`).
- [ ] **Implementa pausas (sé cortés):** No satures el servidor. Introduce pausas deliberadas (`time.sleep()` en Python) entre tus peticiones para simular un ritmo de navegación humano y no degradar el rendimiento del sitio.
- [ ] **Almacena en caché los resultados:** Guarda las páginas que ya has descargado. Si necesitas volver a ejecutar el script, no tendrás que volver a solicitar los mismos recursos, reduciendo la carga sobre el servidor.
- [ ] **Limita las peticiones a horas de bajo tráfico:** Si es posible, ejecuta tus scripts en horarios donde el sitio tenga menos visitantes (ej. por la noche) para minimizar el impacto.
- [ ] **Extrae solo lo que necesitas:** No descargues el sitio web completo si solo te interesan unos pocos datos. Sé específico y eficiente en tu extracción.


## Precedentes: Casos legales

### hiQ Labs v LinkedIn:
""")

st.image(IMG_DIR / "Linkedin vs HiQ.png", caption="Diagrama", use_container_width=True)

st.markdown("""
Este es el caso de referencia sobre la legalidad del web scraping de datos públicos en EE. UU. Inicialmente, el Noveno Circuito falló a favor de hiQ, que extraía datos de perfiles públicos de LinkedIn, considerando que el scraping de datos públicos no violaba la Ley de Fraude y Abuso Informático (CFAA). Sin embargo, el caso tuvo un final más complejo en 2022: hiQ estipuló que LinkedIn podía establecer responsabilidad bajo la CFAA por el acceso directo a páginas protegidas por contraseña usando cuentas falsas, además de violar el Acuerdo de Usuario y ser responsable por interferencia (_Trespass to Chattels_). La lección clave es que el scraping de datos públicos es, por lo general, legal, siempre que no se rompan las barreras de autenticación (inicios de sesión) o los Términos de Servicio (ToS).

### Facebook v. Power Ventures:
""")

st.image(IMG_DIR / "Facebook-v.-Power-Ventures.png", caption="Diagrama", use_container_width=True)

st.markdown("""
Este caso ilustra los múltiples frentes legales que enfrenta un _scraper_. Facebook demandó a Power Ventures por recopilar datos de sus usuarios y mostrarlos en una plataforma competidora. El tribunal falló a favor de Facebook, determinando que Power Ventures había infringido la Ley CAN-SPAM, la CFAA (Ley de Abuso y Fraude Informático), la DMCA (Ley de Derechos de Autor del Milenio Digital) y las leyes de derechos de autor. Este caso demostró que la recopilación de datos de perfiles de usuario puede acarrear responsabilidad no solo por el acceso, sino también por la violación de los derechos de propiedad intelectual y otras leyes cibernéticas.

### Ryanair v. Atrápalo y PR Aviation:

Este caso es fundamental para entender la relación entre el contrato (ToS) y la protección legal de las bases de datos en Europa. Ryanair demandó a Atrápalo por extraer datos de precios y horarios de su sitio web para fines comerciales.

-   **Contrato**: El Tribunal Supremo español dictaminó que, si bien el scraping estaba prohibido en los Términos y Condiciones (T&C) de Ryanair, el scraping de datos era ajeno al objeto principal del contrato (la reserva de vuelos), lo que debilitó el argumento de incumplimiento contractual.

-   **Derecho Sui Generis**: Aunque el Tribunal de Justicia de la Unión Europea (TJUE) confirmó previamente en un caso relacionado con PR Aviation que la Directiva 96/9/CE no prohíbe las limitaciones contractuales si la base de datos no está protegida por _copyright_ o Derecho Sui Generis, la protección clave contra el scraping sistemático en la UE sigue siendo el Derecho Sui Generis, que protege la inversión sustancial en la creación de la base de datos fáctica.


## Conclusiones
El web scraping es una actividad de alto riesgo legal si no se abordan diligentemente sus condiciones. La clave para la legalidad reside en la intersección exitosa de respetar el contrato, evitar el daño a la infraestructura y cumplir con las regulaciones de privacidad y propiedad intelectual.
""")
