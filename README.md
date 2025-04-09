# NLQ to SQL Evaluation Project

This repository contains all the Python scripts and experiments utilized for the evaluation of selected large language models (LLMs) aimed at translating natural language queries (NLQs) to SQL. The experiments detailed within this repository form part of a comprehensive assessment as described in the associated scientific article.

The project focuses on a rigorous evaluation of ten representative LLMs. Each model’s performance is systematically assessed based on its ability to generate syntactically and semantically valid SQL queries from NLQs. The evaluation methodology ensures stability and reproducibility through automated experimentation using Python scripts.

## Project Structure

The repository is organized into the following main folders:

- **DeepSeek**  
  Contains the experimental scripts and data pertaining to the DeepSeek model.

- **GPT 3.0**  
  Includes the Python scripts and evaluation results for the GPT 3.0 model.

- **GPT 3.5**  
  Contains the experimental setup specific to GPT 3.5.

- **GPT 4o**  
  Houses the experiments and related materials for the GPT 4o model.

- **GPT 4o mini**  
  Provides the scripts and data for evaluating the GPT 4o mini variant.

- **GPT o1**  
  Contains the relevant experiments concerning the GPT o1 model.

- **GPT o3 mini**  
  Includes all scripts and results for the GPT o3 mini variant.

- **GPT o3 mini high**  
  Contains the experimental data and scripts for GPT o3 mini high.

- **OLLAMA SQLCoder 7B**  
  Contains the materials for evaluating the OLLAMA SQLCoder model (7B version).

- **OLLAMA SQLCoder 15B**  
  Houses the scripts and evaluation results for the OLLAMA SQLCoder 15B model.

Additionally, the folder named **licenses** includes the distribution licenses for the software components and scripts provided in this repository.

## Experimental Overview

The experiments are designed to assess each LLM’s performance based on their capability to translate NLQs into SQL queries that meet both syntactic and semantic criteria. For each NLQ, the system generates multiple SQL query variants, which are then executed and analyzed to determine performance metrics such as query execution speed and validity relative to expert-generated reference queries. The experimental procedure is automated via a collection of Python scripts, ensuring that the evaluation process remains robust and reproducible across different hardware configurations.

## License

The licensing terms for all scripts and resources in this project can be found in the [licenses](./licenses) directory.

---

This project serves as a foundational framework for the automated evaluation of LLMs in the context of NLQ to SQL translation, contributing to the broader field of data engineering for non-technical users. For more detailed information on specific experiments, refer to the corresponding folders within the repository.
