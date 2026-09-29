import hashlib
import re
import streamlit as st

from ai_extractor import extract_label_data


st.set_page_config(
    page_title="Alcohol Label Verification POC",
    layout="wide"
)

st.title("Alcohol Beverage Label Verification")

st.write(
    "AI-assisted proof-of-concept for comparing alcohol beverage "
    "label artwork against expected application information."
)


def normalize_text(value):
    """
    Normalize capitalization, punctuation, and whitespace for
    general text comparisons.
    """
    if value is None:
        return ""

    text = str(value).casefold().strip()

    # Treat ampersands consistently.
    text = text.replace("&", " and ")

    # Remove punctuation while keeping letters and numbers.
    text = re.sub(r"[^a-z0-9]+", " ", text)

    return " ".join(text.split())


def normalize_country(value):
    """
    Normalize common United States country-name variants.
    """
    normalized = normalize_text(value)

    us_variants = {
        "us",
        "usa",
        "u s",
        "u s a",
        "united states",
        "united states of america"
    }

    if normalized in us_variants:
        return "united states"

    return normalized


def parse_volume_ml(value):
    """
    Convert common mL and L volume formats into milliliters.
    Returns None when no supported volume can be identified.
    """
    if not value:
        return None

    text = str(value).casefold().replace(",", "").strip()

    ml_match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:ml|milliliter|milliliters)",
        text
    )

    if ml_match:
        return float(ml_match.group(1))

    liter_match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:l|liter|liters|litre|litres)\b",
        text
    )

    if liter_match:
        return float(liter_match.group(1)) * 1000

    return None


def parse_alcohol(value):
    """
    Extract ABV percentage and proof values when present.
    """
    if not value:
        return None, None

    text = str(value).casefold()

    abv_match = re.search(
        r"(\d+(?:\.\d+)?)\s*%",
        text
    )

    proof_match = re.search(
        r"(\d+(?:\.\d+)?)\s*proof",
        text
    )

    abv = float(abv_match.group(1)) if abv_match else None
    proof = float(proof_match.group(1)) if proof_match else None

    return abv, proof


def compare_field(field_name, expected, observed):
    """
    Compare application data with extracted label data using
    field-specific normalization.

    Returns:
        MATCH
        MISMATCH
        MISSING
        NEEDS REVIEW
    """

    if not normalize_text(expected):
        return "NOT CHECKED"

    if not normalize_text(observed):
        return "MISSING"

    # Country comparison
    if field_name == "Country of Origin":
        if normalize_country(expected) == normalize_country(observed):
            return "MATCH"

        return "MISMATCH"

    # Net contents comparison
    if field_name == "Net Contents":
        expected_ml = parse_volume_ml(expected)
        observed_ml = parse_volume_ml(observed)

        if expected_ml is not None and observed_ml is not None:
            if abs(expected_ml - observed_ml) < 0.1:
                return "MATCH"

            return "MISMATCH"

    # Alcohol comparison
    if field_name == "Alcohol Content":
        expected_abv, expected_proof = parse_alcohol(expected)
        observed_abv, observed_proof = parse_alcohol(observed)

        comparable_values = 0

        if expected_abv is not None and observed_abv is not None:
            comparable_values += 1

            if abs(expected_abv - observed_abv) > 0.05:
                return "MISMATCH"

        if expected_proof is not None and observed_proof is not None:
            comparable_values += 1

            if abs(expected_proof - observed_proof) > 0.1:
                return "MISMATCH"

        if comparable_values > 0:
            return "MATCH"

    # General text comparison
    if normalize_text(expected) == normalize_text(observed):
        return "MATCH"

    return "MISMATCH"

def validate_government_warning(warning_text):
    """
    Validate the required Government Health Warning text.

    The required wording and punctuation are compared without
    treating OCR capitalization differences in the body text as
    a failure. The GOVERNMENT WARNING heading must still be present
    in uppercase.

    Visual requirements such as bold type, font size, separation,
    and legibility remain reviewer responsibilities.
    """

    if not warning_text or not warning_text.strip():
        return "MISSING"

    required_warning = (
        "GOVERNMENT WARNING: (1) According to the Surgeon General, "
        "women should not drink alcoholic beverages during pregnancy "
        "because of the risk of birth defects. "
        "(2) Consumption of alcoholic beverages impairs your ability "
        "to drive a car or operate machinery, and may cause health problems."
    )

    # Normalize whitespace introduced by OCR or image layout.
    actual = re.sub(r"\s+", " ", warning_text.strip())
    required = re.sub(r"\s+", " ", required_warning)

    # The required heading must actually appear in uppercase.
    if "GOVERNMENT WARNING:" not in actual:
        return "NEEDS REVIEW"

    # Compare required wording without penalizing OCR capitalization
    # differences in the remainder of the warning.
    if required.casefold() in actual.casefold():
        return "MATCH"

    return "NEEDS REVIEW"

def load_extracted_as_application():
    """
    Populate the Application Information fields with the values
    extracted from the uploaded label.

    This is a POC testing helper only. In a production environment,
    expected application data would come from an authoritative
    application system or API.
    """

    data = st.session_state.get("extracted_data", {})

    st.session_state["brand_name_input"] = data.get(
        "brand_name", ""
    )

    st.session_state["class_type_input"] = data.get(
        "class_type", ""
    )

    st.session_state["alcohol_content_input"] = data.get(
        "alcohol_content", ""
    )

    st.session_state["net_contents_input"] = data.get(
        "net_contents", ""
    )

    st.session_state["producer_name_input"] = data.get(
        "producer_name", ""
    )

    st.session_state["producer_address_input"] = data.get(
        "producer_address", ""
    )

    st.session_state["country_of_origin_input"] = data.get(
        "country_of_origin", ""
    )

# ---------------------------------------------------------
# Application information and label artwork
# ---------------------------------------------------------

left_col, right_col = st.columns(2)

with left_col:
    st.subheader("Application Information")

    brand_name = st.text_input(
        "Brand Name",
        placeholder="OLD TOM DISTILLERY",
        key="brand_name_input"
    )

    class_type = st.text_input(
        "Class / Type",
        placeholder="Kentucky Straight Bourbon Whiskey",
        key="class_type_input"
    )

    alcohol_content = st.text_input(
        "Alcohol Content",
        placeholder="45% Alc./Vol. (90 Proof)",
        key="alcohol_content_input"
    )

    net_contents = st.text_input(
        "Net Contents",
        placeholder="750 mL",
        key="net_contents_input"
    )

    producer_name = st.text_input(
        "Bottler / Producer Name",
        placeholder="Old Tom Distillery LLC",
        key="producer_name_input"
    )

    producer_address = st.text_input(
        "Bottler / Producer Address",
        placeholder="123 Bourbon Way, Frankfort, KY",
        key="producer_address_input"
    )

    country_of_origin = st.text_input(
        "Country of Origin",
        placeholder="United States",
        key="country_of_origin_input"
    )

with right_col:
    st.subheader("Label Artwork")

    uploaded_file = st.file_uploader(
        "Upload label artwork",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_file is not None:
        st.image(
            uploaded_file,
            caption="Uploaded label artwork",
            use_container_width=True
        )


# ---------------------------------------------------------
# AI extraction
# ---------------------------------------------------------

st.divider()
st.subheader("AI Label Extraction")

if uploaded_file is not None:

    # Create a fingerprint so results from an old image are not
    # accidentally used after a different image is uploaded.
    image_hash = hashlib.sha256(
        uploaded_file.getvalue()
    ).hexdigest()

    if (
        st.session_state.get("image_hash")
        and st.session_state["image_hash"] != image_hash
    ):
        st.session_state.pop("extracted_data", None)

    st.session_state["image_hash"] = image_hash

    if st.button(
        "Extract Label Information with AI",
        type="primary"
    ):
        try:
            with st.spinner("Analyzing label artwork..."):
                extracted_data = extract_label_data(uploaded_file)

            st.session_state["extracted_data"] = extracted_data
            st.success("AI extraction completed.")

        except Exception as exc:
            st.error(
                "AI extraction failed. "
                f"Technical detail: {exc}"
            )

else:
    st.info("Upload label artwork to enable AI extraction.")


# ---------------------------------------------------------
# Display AI extraction
# ---------------------------------------------------------

extracted_data = st.session_state.get("extracted_data")

if extracted_data:

    st.write("### Extracted Label Information")

    extraction_rows = [
        {
            "Field": "Brand Name",
            "Extracted Value": extracted_data.get("brand_name", "")
        },
        {
            "Field": "Class / Type",
            "Extracted Value": extracted_data.get("class_type", "")
        },
        {
            "Field": "Alcohol Content",
            "Extracted Value": extracted_data.get(
                "alcohol_content", ""
            )
        },
        {
            "Field": "Net Contents",
            "Extracted Value": extracted_data.get(
                "net_contents", ""
            )
        },
        {
            "Field": "Producer Name",
            "Extracted Value": extracted_data.get(
                "producer_name", ""
            )
        },
        {
            "Field": "Producer Address",
            "Extracted Value": extracted_data.get(
                "producer_address", ""
            )
        },
        {
            "Field": "Country of Origin",
            "Extracted Value": extracted_data.get(
                "country_of_origin", ""
            )
        },
        {
            "Field": "Government Warning",
            "Extracted Value": extracted_data.get(
                "government_warning_text", ""
            )
        }
    ]

    st.table(extraction_rows)
    st.info(
        "POC Test Helper: In a production environment, expected "
        "application data would come from the authoritative application "
        "system. For demonstration purposes, you can initialize a test "
        "application from the extracted label values and then modify "
        "individual fields to test discrepancy detection."
    )

    st.button(
        "Create Test Application from Extracted Label",
        on_click=load_extracted_as_application,
        use_container_width=True
    )

# ---------------------------------------------------------
# Manual developer test harness
# ---------------------------------------------------------

st.divider()

use_manual_data = st.checkbox(
    "Developer mode: use manually entered extraction data"
)

manual_data = {}

if use_manual_data:

    with st.expander(
        "Developer Test Harness",
        expanded=True
    ):

        st.caption(
            "Manual fallback for testing comparison logic "
            "without making an AI API request."
        )

        manual_data["brand_name"] = st.text_input(
            "Observed Brand Name"
        )

        manual_data["class_type"] = st.text_input(
            "Observed Class / Type"
        )

        manual_data["alcohol_content"] = st.text_input(
            "Observed Alcohol Content"
        )

        manual_data["net_contents"] = st.text_input(
            "Observed Net Contents"
        )

        manual_data["producer_name"] = st.text_input(
            "Observed Producer Name"
        )

        manual_data["producer_address"] = st.text_input(
            "Observed Producer Address"
        )

        manual_data["country_of_origin"] = st.text_input(
            "Observed Country of Origin"
        )

        manual_data["government_warning_text"] = st.text_area(
            "Observed Government Health Warning Text",
            height=120,
            placeholder="Enter extracted warning text for manual testing."
        )


# ---------------------------------------------------------
# Verification
# ---------------------------------------------------------

st.divider()

analyze_button = st.button(
    "Compare Application Against Label",
    use_container_width=True
)

if analyze_button:

    if uploaded_file is None:
        st.error("Please upload label artwork before analysis.")

    elif not brand_name.strip():
        st.error("Please enter the expected brand name.")

    elif not use_manual_data and not extracted_data:
        st.error(
            "Run AI extraction before comparing the label."
        )

    else:

        expected_data = {
            "Brand Name": brand_name,
            "Class / Type": class_type,
            "Alcohol Content": alcohol_content,
            "Net Contents": net_contents,
            "Producer Name": producer_name,
            "Producer Address": producer_address,
            "Country of Origin": country_of_origin
        }

        source_data = (
            manual_data
            if use_manual_data
            else extracted_data
        )

        observed_data = {
            "Brand Name": source_data.get(
                "brand_name", ""
            ),
            "Class / Type": source_data.get(
                "class_type", ""
            ),
            "Alcohol Content": source_data.get(
                "alcohol_content", ""
            ),
            "Net Contents": source_data.get(
                "net_contents", ""
            ),
            "Producer Name": source_data.get(
                "producer_name", ""
            ),
            "Producer Address": source_data.get(
                "producer_address", ""
            ),
            "Country of Origin": source_data.get(
                "country_of_origin", ""
            )
        }

        warning_text = source_data.get(
            "government_warning_text",
    
            ""
        )

        warning_status = validate_government_warning(
            warning_text
        )

        st.subheader("Verification Results")

        statuses = []

        for field_name in expected_data:

            expected = expected_data[field_name]
            observed = observed_data[field_name]

            status = compare_field(
                field_name,
                expected,
                observed
            )

            statuses.append(status)

            col1, col2, col3, col4 = st.columns(
                [2, 3, 3, 2]
            )

            col1.write(f"**{field_name}**")
            col2.write(
                expected if expected else "Not provided"
            )
            col3.write(
                observed if observed else "Not detected"
            )

            if status == "MATCH":
                col4.success("MATCH")

            elif status == "MISSING":
                col4.warning("MISSING")

            elif status == "NEEDS REVIEW":
                col4.warning("NEEDS REVIEW")

            elif status == "NOT CHECKED":
                col4.info("NOT CHECKED")

            else:
                col4.error("MISMATCH")

        st.divider()

        st.write("**Government Health Warning**")

        if warning_status == "MATCH":
            st.success("WARNING TEXT VERIFIED")

        elif warning_status == "MISSING":
            st.error("MISSING")

        else:
            st.warning("NEEDS REVIEW")

        if warning_text:
            with st.expander("View Extracted Government Warning"):
                st.write(warning_text)

        st.caption(
            "Automated validation evaluates extracted warning content. "
            "Visual formatting and regulatory presentation should be "
            "confirmed by a reviewer."
        )

        st.divider()

        if (
            all(
                status in {"MATCH", "NOT CHECKED"}
                for status in statuses
            )
            and warning_status == "MATCH"
        ):
            st.success(
                "No discrepancies detected in application fields provided. "
                "Reviewer verification is still required."
            )
        else:
            st.warning(
                "Reviewer attention required. "
                "One or more discrepancies, missing elements, "
                "or warning-content issues were detected."
            )