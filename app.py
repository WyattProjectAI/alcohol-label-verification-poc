import streamlit as st

# Configure browser tab and page layout.
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
    Normalize text before comparison so harmless differences in
    capitalization or spacing do not create false mismatches.
    """
    if value is None:
        return ""

    return " ".join(str(value).strip().lower().split())


def compare_field(expected, observed):
    """
    Compare an expected application value with a value extracted
    from label artwork.

    Returns:
        MATCH        - Values are equivalent after normalization.
        MISSING      - No value was found on the label.
        MISMATCH     - A different value was found.
    """
    expected_normalized = normalize_text(expected)
    observed_normalized = normalize_text(observed)

    if not observed_normalized:
        return "MISSING"

    if expected_normalized == observed_normalized:
        return "MATCH"

    return "MISMATCH"


# -------------------------------------------------------------------
# Application information
# -------------------------------------------------------------------

left_col, right_col = st.columns(2)

with left_col:
    st.subheader("Application Information")

    brand_name = st.text_input(
        "Brand Name",
        placeholder="OLD TOM DISTILLERY"
    )

    class_type = st.text_input(
        "Class / Type",
        placeholder="Kentucky Straight Bourbon Whiskey"
    )

    alcohol_content = st.text_input(
        "Alcohol Content",
        placeholder="45% Alc./Vol. (90 Proof)"
    )

    net_contents = st.text_input(
        "Net Contents",
        placeholder="750 mL"
    )

    producer_name = st.text_input(
        "Bottler / Producer Name",
        placeholder="Old Tom Distillery LLC"
    )

    producer_address = st.text_input(
        "Bottler / Producer Address",
        placeholder="123 Bourbon Way, Frankfort, KY"
    )

    country_of_origin = st.text_input(
        "Country of Origin",
        placeholder="United States"
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

        st.success("Label image uploaded successfully.")


# -------------------------------------------------------------------
# Temporary manual extraction test harness
# -------------------------------------------------------------------

st.divider()

with st.expander("Developer Test Harness: Simulated Label Extraction"):
    st.caption(
        "Temporary testing controls. These fields simulate values that "
        "will later be extracted automatically by the AI model."
    )

    observed_brand = st.text_input(
        "Observed Brand Name",
        key="observed_brand"
    )

    observed_class = st.text_input(
        "Observed Class / Type",
        key="observed_class"
    )

    observed_alcohol = st.text_input(
        "Observed Alcohol Content",
        key="observed_alcohol"
    )

    observed_net = st.text_input(
        "Observed Net Contents",
        key="observed_net"
    )

    observed_producer = st.text_input(
        "Observed Bottler / Producer Name",
        key="observed_producer"
    )

    observed_address = st.text_input(
        "Observed Bottler / Producer Address",
        key="observed_address"
    )

    observed_country = st.text_input(
        "Observed Country of Origin",
        key="observed_country"
    )

    government_warning_found = st.checkbox(
        "Government Health Warning found on label"
    )


# -------------------------------------------------------------------
# Analysis
# -------------------------------------------------------------------

st.divider()

analyze_button = st.button(
    "Analyze Label",
    type="primary",
    use_container_width=True
)

if analyze_button:

    if uploaded_file is None:
        st.error("Please upload label artwork before analysis.")

    elif not brand_name.strip():
        st.error("Please enter the expected brand name.")

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

        observed_data = {
            "Brand Name": observed_brand,
            "Class / Type": observed_class,
            "Alcohol Content": observed_alcohol,
            "Net Contents": observed_net,
            "Producer Name": observed_producer,
            "Producer Address": observed_address,
            "Country of Origin": observed_country
        }

        st.subheader("Verification Results")

        statuses = []

        for field_name in expected_data:
            expected = expected_data[field_name]
            observed = observed_data[field_name]

            status = compare_field(expected, observed)
            statuses.append(status)

            col1, col2, col3, col4 = st.columns([2, 3, 3, 2])

            col1.write(f"**{field_name}**")
            col2.write(expected if expected else "Not provided")
            col3.write(observed if observed else "Not detected")

            if status == "MATCH":
                col4.success("MATCH")
            elif status == "MISSING":
                col4.warning("MISSING")
            else:
                col4.error("MISMATCH")

        st.divider()

        st.write("**Government Health Warning**")

        if government_warning_found:
            st.success("FOUND")
        else:
            st.warning("NEEDS REVIEW")

        # A reviewer should make the final compliance determination.
        # The prototype identifies discrepancies rather than allowing
        # the AI model to make an authoritative approval decision.
        if (
            all(status == "MATCH" for status in statuses)
            and government_warning_found
        ):
            st.success(
                "Label verification completed with no detected discrepancies."
            )
        else:
            st.warning(
                "Label requires reviewer attention. "
                "One or more discrepancies or missing elements were detected."
            )