# Ontología de Infraestructura Pública

La ontología de Infraestructura Pública representa los datos de las instalaciones (equipamientos) de un municipio. Estos incluyen centros educativos, sociales y culturales, deportivos, así como aparcamientos dentro y fuera de la vía pública y estaciones de bicicletas compartidas.


# Propósito y alcance de la ontología (Purpose and scope of the ontology)

El propósito de esta ontología es el de proporcionar un vocabulario común para la representación de las entidades y datos principales de la infraestructura pública de un municipio que pueden incluir tanto centros educativos, centros culturales y sociales, centros de salud así como todo los aparcamoientos dentro y fuera de la vía pública. Su alcance se limita a los datos que pueden ser utilizados con los propósitos de mantener y acceder al inventario de los equipamientos municipales y conocer su consumo de recursos (electricidad, agua, etc.), de gestionar el mantenimiento urbano, el de la gestión de la movilidad (accesos a las instalaciones municipales y accesos de vehículos a los aparcamientos), que son parte de las funciones habituales de las entidades locales.

# Prefijo y espacio de nombres (Prefix and namespace)
El prefijo de la ontología de Infraestructura Pública es: edintinfp y es publicada en el espacio de nombres: [http://vocab.linkeddata.es/datosabiertos/def/urbanismo-infraestructuras/infraestructurapublica#](http://vocab.linkeddata.es/datosabiertos/def/urbanismo-infraestructuras/infraestructurapublica#) 

# Modelo conceptual (Ontology conceptualization)
![Modelo conceptual general](diagrams/diagramGeneral.png)
![Modelo conceptual de aparcamiento](diagrams/diagramAparcamiento.png)

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

# Project maintenance

To manage those incidents or suggested improvements with respect to the vocabulary, we recommend you to follow
the guides provided in [Issues Management](https://github.com/nombre-repositorio/wiki/issues-management) to
generate an issue (work in progress)

# Funding

Esta ontología ha sido desarrollada en el contexto del Espacio de Datos para las Infraestructuras Urbanas Inteligentes (EDINT).
