# Ontología de Infraestructura (The Infrastructure Ontology)

La ontología de Infraestructura representa los datos de las instalaciones (equipamientos) de un municipio. Estos incluyen centros educativos, sociales y culturales, deportivos, así como aparcamientos dentro y fuera de la vía pública y estaciones de bicicletas compartidas.


# Propósito y alcance de la ontología (Purpose and scope of the ontology)

El propósito de esta ontología es el de proporcionar un vocabulario común para la representación de las entidades y datos principales de la infraestructura de un municipio que pueden incluir tanto centros educativos, centros culturales y sociales, centros de salud así como todo los aparcamoientos dentro y fuera de la vía pública. Su alcance se limita a los datos que pueden ser utilizados con los propósitos de mantener y acceder al inventario de los equipamientos municipales y conocer su consumo de recursos (electricidad, agua, etc.), de gestionar el mantenimiento urbano, el de la gestión de la movilidad (accesos a las instalaciones municipales y accesos de vehículos a los aparcamientos), que son parte de las funciones habituales de las entidades locales.

# Prefijo y espacio de nombres (Prefix and namespace)
El prefijo de la ontología de Infraestructura es: edintinf y es publicada en el espacio de nombres: [http://vocab.linkeddata.es/datosabiertos/def/urbanismo-infraestructuras/infraestructura#](http://vocab.linkeddata.es/datosabiertos/def/urbanismo-infraestructuras/infraestructura#) 

# Modelo conceptual (Ontology conceptualization)
![Modelo conceptual general](diagrams/diagrama-conceptual-General.png)

![Modelo conceptual general](diagrams/diagrama-conceptual-AccessSensors.png)

![Modelo conceptual general](diagrams/diagrama-conceptual-CountingSensors.png)

![Modelo conceptual general](diagrams/diagrama-conceptual-TrafficSensors.png)

# Estructura del repositorio (Repository structure)

El repositorio contiene los siguientes directorios:

| Folder | Description |
|--------|--------------|
| **diagrams/** | Stores diagrams and other resources representing the conceptual model of the ontology (e.g., class hierarchies, relationships). |
| **documentation/** | Stores the HTML or human oriented documentation of the ontology and related artefacts. |
| **examples/** | Includes examples that demonstrate how to instantiate or apply the ontology in real data scenarios. |
| **kos/** | Stores controlled vocabularies or KOS implementation, usually SKOS implementations in rdf. |
| **ontology/** | Contains the actual ontology implementation files in formats such as `.owl`, `.rdf`, `.ttl`, or `.jsonld`. |
| **requirements/** | Contains all documents used to define the ontology’s requirements: data example, competency questions, functional requirements, use cases, etc. |
| **shapes/** | Contains the SHACL shapes used to define and validate ontology constraints. |

# Mantenimiento y evolución (Maintenance and evolution)

Para manejar las incidencias o mejoras sugeridas con respecto a la ontología, recomendamos seguir las guía proporcionadas en ([Issues Management](https://github.com/telefonicasc/edint-ontologia-infraestructura/issues)) para generar una indicencia (trabajo en progreso).

# Financiación (Funding)

Esta ontología ha sido desarrollada en el contexto del Espacio de Datos para las Infraestructuras Urbanas Inteligentes ([EDINT](https://edint.es)).

![Logos](EDINT_UE_V-Color.png)

