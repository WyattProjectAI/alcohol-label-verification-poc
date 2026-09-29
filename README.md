# Alcohol Beverage Label Verification POC

An AI-assisted proof-of-concept for comparing alcohol beverage label artwork against expected application information.

## Live Application

The deployed proof-of-concept is available at:

https://alcohol-label-verification-poc.streamlit.app/

## Purpose

This prototype demonstrates how artificial intelligence can assist a reviewer by extracting information from alcohol beverage label artwork and comparing the extracted information with expected application data.

The system is designed to support, not replace, human review.

## Verification Workflow

1. User enters expected application information.
2. User uploads alcohol beverage label artwork.
3. An AI vision model extracts structured label information.
4. Python normalization logic compares expected and observed values.
5. The application identifies matches, mismatches, missing information, and items requiring review.
6. Government Health Warning text is independently evaluated for expected content.
7. A reviewer makes the final determination.

## Architecture

The prototype intentionally separates AI extraction from verification logic.

### AI Layer

The AI model performs visual extraction of:

- Brand name
- Class or type
- Alcohol content
- Net contents
- Producer or bottler information
- Address
- Country of origin
- Government Health Warning text

The model does not approve or reject a label.

### Deterministic Verification Layer

Python logic evaluates extracted values using field-specific normalization.

Examples include:

- Capitalization and punctuation normalization
- Country-name normalization
- Alcohol percentage and proof comparison
- Liter and milliliter conversion
- Government Health Warning content verification

This design reduces reliance on nondeterministic model judgment for final verification decisions.

## Technologies

- Python
- Streamlit
- OpenAI Responses API
- Structured Outputs
- Multimodal image analysis
- Pillow
- python-dotenv
- GitHub

## Repository Structure

- `app.py` - Streamlit user interface, normalization, comparison, and verification logic
- `ai_extractor.py` - AI-assisted image analysis and structured label-data extraction
- `requirements.txt` - Python project dependencies
- `.gitignore` - Excludes local environments, API credentials, and other non-source files
- `examples/` - Example alcohol label images provided for demonstration and testing

Tested with Python 3.13.3.

## Local Setup

Clone the repository and create a Python virtual environment.

```powershell
python -m venv .venv
```

Activate the virtual environment on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install project dependencies:

```powershell
pip install -r requirements.txt
```

If setting up the project on a new machine, create a local `.env` file in the repository root using your own API credentials:

```text
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-6-luna
```

Do not commit the `.env` file to GitHub.

Run the application:

```powershell
streamlit run app.py
```

The application will normally be available at:

```text
http://localhost:8501
```

## Using the Prototype

1. Upload alcohol beverage label artwork in PNG or JPEG format.
2. Select **Extract Label Information with AI**.
3. Review the information extracted from the artwork.
4. Enter expected application information manually, or select **Create Test Application from Extracted Label** to initialize demonstration data.
5. When using the POC Test Helper, modify one or more Application Information fields if you want to test discrepancy detection.
6. Select **Compare Application Against Label**.
7. Review each field for Match, Mismatch, Missing, Not Checked, or Needs Review status.
8. Review the Government Health Warning validation result.
9. A human reviewer makes the final determination.

### POC Test Helper

The deployed prototype is not integrated with COLAs Online or another authoritative application database.

For demonstration purposes, **Create Test Application from Extracted Label** initializes the Application Information fields using values extracted from the uploaded artwork. A reviewer can then change individual expected values to verify mismatch and missing-data detection.

In a production implementation, expected application information would be retrieved independently from the authoritative application system rather than generated from the label being reviewed.

## Example Test Labels

Two example label images are included in the `examples/` directory for demonstration and testing:

- `sample-lager-label.png` - Example lager label containing brand, beverage type, alcohol content, net contents, producer information, country information, and Government Health Warning text.
- `sample-craft-ale-label.png` - Example craft beer label used to demonstrate extraction when some expected application information may not be detected. Missing or unavailable expected information may be reported as `NOT CHECKED` rather than being inferred.

These examples are provided to make it easier to test the prototype without locating separate label artwork.

A reviewer may upload either example, run AI extraction, use **Create Test Application from Extracted Label**, and then modify one or more Application Information fields to test discrepancy detection.

## Developer Test Mode

The application includes a manual developer test mode that allows extracted values to be entered manually.

This makes it possible to test normalization, comparison logic, missing values, mismatches, and Government Health Warning validation without making additional AI API requests.

## Security Considerations

API credentials are not stored in source code.

The following files are excluded from Git through `.gitignore`:

```text
.env
.streamlit/secrets.toml
```

For a hosted deployment, API credentials should be stored using the hosting platform's secret-management functionality.

Uploaded label artwork is transmitted to the configured AI service for analysis.

A production implementation would require additional controls such as:

- Authentication and authorization
- Centralized secret management
- Audit logging
- Data-retention policies
- Encryption requirements
- Monitoring and alerting
- API access controls
- Rate limiting
- Security testing
- Formal privacy and compliance review

## Error Handling

The prototype includes handling for:

- Missing label artwork
- Missing expected application data
- AI extraction failures
- Missing extracted information
- Mismatched application and label values
- Incomplete Government Health Warning content

## Human-in-the-Loop Design

The AI model performs information extraction but does not make the final compliance or approval decision.

Deterministic Python logic performs field comparison and identifies discrepancies.

The application intentionally presents results to a reviewer rather than automatically approving or rejecting submitted artwork.

This architecture limits reliance on nondeterministic AI output for regulatory decision-making.

## Assumptions

This application is a proof-of-concept rather than a production regulatory system.

The prototype assumes:

- Submitted artwork is sufficiently readable for image analysis.
- AI extraction may occasionally be incomplete or inaccurate.
- Expected application data is provided by the user.
- Human reviewers remain responsible for final verification.
- Regulatory visual-formatting requirements may require manual inspection.

## Known Limitations

The prototype does not:

- Make regulatory approval decisions.
- Replace human review.
- Validate every alcohol-label regulatory requirement.
- Guarantee AI or OCR extraction accuracy.
- Persist application information to a database.
- Implement production identity and access management.
- Implement enterprise audit logging.
- Evaluate every visual presentation requirement automatically.
- Requires outbound access to the configured AI API; restricted networks may prevent AI extraction.
- Processes one label at a time; batch processing is a potential future enhancement.

## Testing

The prototype was tested using multiple alcohol beverage labels containing:

- Multiple label panels
- Rotated text
- Small regulatory text
- Alcohol-content information
- Net-content information
- Producer information
- Country-of-origin information
- Government Health Warning text

The included test files are:

- `examples/sample-lager-label.png`
- `examples/sample-craft-ale-label.png`

Testing included:

- Successful field matches
- Intentional field mismatches
- Missing extracted information
- `NOT CHECKED` handling when expected information is unavailable
- Government Health Warning validation
- AI extraction from differently formatted label artwork
- AI extraction completing in under five seconds during local testing

The craft beer example also demonstrates that the application does not invent unavailable information when a field cannot be confidently extracted.

## AI-Assisted Development

AI-assisted development tools were used during implementation for code generation, troubleshooting, documentation, and iterative testing.

Architecture decisions, implementation review, testing, validation, and final project submission were performed and reviewed by the developer.

## Project Status

Working proof-of-concept supporting:

- Image upload
- AI-assisted structured extraction
- Deterministic field comparison
- Field-specific normalization
- Government Health Warning validation
- Manual developer testing
- Human-review-oriented results

Deployed application:

https://alcohol-label-verification-poc.streamlit.app/