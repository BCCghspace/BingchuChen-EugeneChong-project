# Project Proposal

**Team Members:** Bingchu Chen, Eugene Chong

## Abstract

The [SafeGraph Core Places](https://docs.safegraph.com/v4.0/docs#section-core-places) dataset and the amenities recorded in OpenStreetMap are two very different sources of point-of-interest data. SafeGraph's data is proprietary and highly curated. The company charges a fee for access to the data, maintains numerous attributes for each POI (with [impressive fill rates](https://docs.safegraph.com/v4.0/docs/places-summary-statistics)), and publishes updated versions of the data monthly. OpenStreetMap, on the other hand, is free and entirely crowd-sourced. While OSM's mapping community attempts to maintain standards for the data listed on OpenStreetMap, and corporate contributors have employees whose primary job is to update the map, OSM's data can vary significantly in completion and accuracy, depending on feature being mapped and the location.

For our project, we’re interested in creating a tool that will allow users to compare the POI data coverage of the SafeGraph Core Places dataset and the amenities recorded in OpenStreetMap. For example, a user could query “coffeeshops in Philadelphia”, and the app would return two maps - one displaying the Philadelphia coffeeshops listed in SafeGraph, and another with the coffeeshops from OSM - along with relevant summary statistics. The user could also use the app to aggregate the coffeeshops to some geographic unit of analysis (TBD) to identify where the data sources differ most in their coverage.

We have two use cases in mind:

1.	The primary use case is for contributors to OpenStreetMap who need assistance identifying gaps in local OSM amenity coverage. If a local mapper has taken up the cause of mapping all of the restaurants in a given city, they could use this tool to identify the areas of the city that require more mapping attention.

2.	A secondary use case is for organizations that are interested in performing geospatial analyses with POI data but are unsure if they need to pay for expensive data from SafeGraph. This tool would help these organizations compare the datasets in their area of interest and get a sense of how much additional value the SafeGraph data would provide.

## Data Sources

1.	**SafeGraph Core Places:**

	* **Access:** Yes, through the SafeGraph COVID-19 Data Consortium
	* **Size of Dataset:** Nationwide, approximately 6MM rows
	* **How to host:** to-be-discussed with Andy

2.	**OpenStreetMap:**

	* **Access:** Yes, through BigQuery
	* **Size of Dataset:** N/A
	* **How to host:** BigQuery

## Wireframes / Mock-ups

![](IMG_4721 "Wireframe")