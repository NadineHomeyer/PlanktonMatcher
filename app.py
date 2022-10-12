import pandas as pd
import numpy as np
import streamlit as st
import datetime
import time
from st_clickable_images import clickable_images

def increment_counter():
    """Incremention session state value"""
    st.session_state.counter += 1

# Function from https://gist.github.com/treuille/2ce0acb6697f205e44e3e0f576e810b7
def paginator(label, items, items_per_page=50):
    """Lets the user paginate a set of items.
    Parameters
    ----------
    label : str
        The label to display over the pagination widget.
    items : Iterator[Any]
        The items to display in the paginator.
    items_per_page: int
        The number of items to display per page.
    on_sidebar: bool
        Whether to display the paginator widget on the sidebar.
        
    Returns
    -------
    Iterator[Tuple[int, Any]]
        An iterator over *only the items on that page*, including
        the item's index.
    """

    # Display a pagination selectbox in the specified location.
    items = list(items)
    n_pages = len(items)
    n_pages = (len(items) - 1) // items_per_page + 1
    page_format_func = lambda i: "Page %s" % i
    page_number = st.sidebar.selectbox(label, range(n_pages), format_func=page_format_func)

    # Iterate over the items in the page to let the user display them.
    min_index = page_number * items_per_page
    max_index = min_index + items_per_page
    import itertools
    return itertools.islice(enumerate(items), min_index, max_index)


# Formatting
st.set_page_config(
    page_title='PhyloMatcher',
    layout='wide',
    page_icon=':fish:',
    initial_sidebar_state="collapsed",
)


if __name__ == '__main__':
    # Handle session
    if 'counter' not in st.session_state:
        st.session_state.counter = 0

    # Remove space at top of page
    st.markdown('<style>div.block-container{padding-top:0.5rem;}</style>', unsafe_allow_html=True)

    # Add filters/input widgets with tooltips
    st.sidebar.markdown("<b>Filters:</b>", unsafe_allow_html=True)
    selected_group = st.sidebar.radio("Oganism group: ", options=('Copepoda', 'Bacillariophyceae', 'Dinophyceae', \
        'Gastropoda', 'Globothalamea', 'Hydrozoa', 'Malacostraca', 'Polychaeta', 'Other'), index=0)
    st.sidebar.markdown("#")

    # Header
    st.markdown("<h1><font color='darkblue'>Plankton Organisms in the region of Aguilas</font></h1>", unsafe_allow_html=True)
    st.write("The plankton organisms listed below have been observed in the region of Aguilas in the past. "
            +"Please look through the list of organisms and read the information given on the linked pages. ")
    st.write("The group of Copepods is displayed per default. Other groups can be displayed by selecting"
            "the radio button of the respective taxon group in the sidebar.")
    st.write("In order to keep the loading time low only 50 images are shown on a page. You can switch between pages "
             "by selecting the corresponding page from the drop-down list in the sidebar. Upon clicking on an image "
             "a larger version of the image and more information about the displayed species is shown at the bottom "
             "of the page.")

    # Read information from individual files with meta-information
    df = pd.read_csv("./marine_plankton.txt", sep="\t")

    # Filtering
    assoc_dict = {"Copepoda" : "Copepoda", \
                "Bacillariophyceae" : "Bacillariophyceae", \
                "Dinophyceae" : "Dinophyceae", \
                "Gastropoda" : "Gastropoda", \
                "Globothalamea" : "Globothalamea", \
                "Hydrozoa" : "Hydrozoa", \
                "Malacostraca" : "Malacostraca", \
                "Polychaeta" : "Polychaeta", \
                "Other": "other"}
    groups = ["Copepoda", "Bacillariophyceae", "Dinophyceae", "Gastropoda", "Globothalamea", \
            "Hydrozoa", "Malacostraca", "Polychaeta", "other"]
    if assoc_dict[selected_group] != "other":
        df = df.loc[df["Group"]==assoc_dict[selected_group], :]
    else:
        df = df.loc[~df["Group"].isin(groups), :]

    # Read NCBI information
    df_ncbi = pd.read_csv("./marine_plankton_NCBItaxreport.txt", sep="|", engine="python")
    df_ncbi = df_ncbi.drop("code\t" ,axis=1)
    df_ncbi = df_ncbi.drop("\tpreferred name\t" ,axis=1)
    df_ncbi = df_ncbi.rename(columns={"\ttaxid": "taxid", "\tname\t": "taxname"})
    df_ncbi["taxname"] = df_ncbi["taxname"].replace(to_replace ='\t', value = '', regex=True)
    df_ncbi["taxid"] = df_ncbi["taxid"].replace(to_replace ='\t', value = '', regex=True)

    # Define columns
    image_links = list(df["ImageLink"])
    species_names = list(df["ScientificName"])
    
    st.sidebar.markdown("<b>Pages with images:</b>", unsafe_allow_html=True)
    image_iterator = paginator("Select a page", image_links)
    indices_on_page, images_on_page = map(list, zip(*image_iterator))

    clicked = clickable_images( images_on_page, indices_on_page,\
                                div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"}, \
                                img_style={"object-fit": "contain", "max-width": "180px", "max-height": "200 px", "margin": "15px", "width": "auto", "height": "auto"})
 
    # Display detailed information upon click
    if clicked > -1:
        page_number = (max(indices_on_page)+1)/50
        if page_number > 1:
            clicked = int(clicked + ((page_number-1)*50))
        # Make sure that there is some space before the detailed species information
        st.markdown("#")
        st.markdown("#")

        # Display detailed sepcies information
        st.subheader(df.iloc[clicked, 0])
        st.image(df.iloc[clicked, 2], width=600)
    
        # Link to GBIF
        df_worms_tmp = df.iloc[clicked, 1]
        if df_worms_tmp != 0:
            worms_link='WoRMS: [Link]({link})'.format(link="https://www.marinespecies.org/aphia.php?p=taxdetails&id="+str(df.iloc[clicked, 1]))
            st.markdown(worms_link, unsafe_allow_html=True)
        # Link to NCBI
        df_ncbi_tmp = df_ncbi.loc[df_ncbi["taxname"]==df.iloc[clicked, 0], :]
        if not(df_ncbi_tmp.empty):
            ncbi_link='NCBI Taxonomy: [Link]({link})'.format(link="https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id="+str(list(df_ncbi_tmp["taxid"])[0]))
            st.markdown(ncbi_link, unsafe_allow_html=True)