# CosmoBoard
Live site: https://t8vlbhpkph.execute-api.eu-north-1.amazonaws.com/Dev/ (may not reflect the latest version)<br>
Note: This GitHub repository contains the most recent code and updates.

The NASA-Cosmoboard Space Biology Dashboard is part of the 2025 NASA Space Apps Challenge. It aims to provide scientists, mission planners, and managers with a dynamic interface to explore and summarize decades of NASA bioscience publications. This project uses a context-aware search engine that compiles research papers, links each to its underlying NASA datasets, and recommends similar publications, and presents a user-friendly layout for accessing all related research with Space Biology topics.

## Project Details
Our Project connects NASA's Space Biology publications with the datasets they reference, creating an intelligent search engine that helps researchers and STEM enthusiasts easily access and explore research. We used a Flask-based backend, hosted on AWS Lambda, with a SQLite database to allow users to search publications by keywords and view a dynamically linked table. The website also runs a TF-IDF based ML recommender system to suggest the top 5 publications the user might be interested in, which saves the researcher valuable time. Our time transformed NASA archives into an interactive research network by focusing on accessibility, scalability, and ethical AI use to make an engaging user experience and make scientific discovery more collaborative.

## Tech Stack
Python, HTML, CSS, Flask, and AWS Lambda

## Use of Artificial Intelligence
After developing the frontend and backend independently, we used Cursor’s AI assistance to help integrate the recommender ML model into the Flask container, ensuring each publication had its own page and relevant recommendations.

## NASA Data
[NASA OSDR: Open Science for Life in Space](https://osdr.nasa.gov/bio/repo/search?q=&data_source=cgene,alsda,esa&data_type=study)<br>
[SB_Publications](https://github.com/jgalazka/SB_publications)

## 💾 Database Tables
### Publications
| Column Name | Data Type | Description                                       |
| ----------- | --------- | ------------------------------------------------- |
| id          | TEXT      | Holds the PMCid of the Space Biology Publications |
| title       | TEXT      | Title of the Space Biology Publication            |

### Datasets
| Column Name | Data Type | Description                                       |
| ----------- | --------- | ------------------------------------------------- |
| id          | TEXT      | Holds the id of the Datasets from the NASA OSDR   |
| title       | TEXT      | Title of the Dataset                              |

### Keywords
| Column Name | Data Type | Description                                       |
| ----------- | --------- | ------------------------------------------------- |
| id          | INTEGER   | Unique identifier for each keyword                |
| keyword     | TEXT      | Keywords recognized to search publications        |

### Referencing
| Column Name    | Data Type | Description                                       |
| -------------- | --------- | ------------------------------------------------- |
| id             | INTEGER   | Unique identifier for the referencing             |
| publication_id | TEXT      | References `Publications(id)`                     |
| dataset_id     | TEXT      | References `Datasets(id)`                         |
| keyword_id     | INTEGER   | References `Keywords(id)`                         |