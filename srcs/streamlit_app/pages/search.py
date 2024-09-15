import os
import sys
import streamlit as st
from elasticsearch import Elasticsearch
sys.path.append('srcs')
from streamlit_app import utils, templates


def app():
    """ search layout """
    # load css
    index = os.environ['INDEX']
    page_size = int(os.environ['PAGE_SIZE'])
    domain = os.environ['DOMAIN']
    port = int(os.environ['PORT'])
    es = Elasticsearch(host=domain, port=port)
    if not es.ping():
        raise ConnectionError(f"Unable to connect to Elasticsearch: {domain}, {port}")
    st.title('Search GRID Records')
    form = st.form("my form")
    if st.session_state.search_name is None:
        search_name = form.text_input('Enter Name (*):')
        search_address = form.text_input('Enter Address:')
        search_dob = form.text_input('Enter DOB (dd/mm/yyyy):')
        submit = form.form_submit_button()
    else:
        search_name = form.text_input('Enter Name (*):', st.session_state.search_name.strip())
        search_address = form.text_input('Enter Address:', st.session_state.search_address.strip()) \
            if st.session_state.search_address else form.text_input('Enter Address:')
        search_dob = form.text_input('Enter DOB (dd/mm/yyyy):', st.session_state.search_dob.strip()) \
            if st.session_state.search_dob else form.text_input('Enter DOB (dd/mm/yyyy):')
        submit = form.form_submit_button()

    if submit or st.session_state.search_name:
        # reset tags when receive new search words
        if not search_name:
            st.write(templates.no_name_html(), unsafe_allow_html=True)
        else:
            if search_name != st.session_state.search_name:
                st.session_state.tags = None
            # reset search word
            #st.session_state.search_name = None
            #st.session_state.search_address = None
            #st.session_state.search_dob = None
            if submit:
                st.session_state.page = 1
            from_i = (st.session_state.page - 1) * page_size
            results = utils.index_search(es, index, search_name, search_address, search_dob, st.session_state.tags,
                                        from_i, page_size)
            total_hits = results['aggregations']['match_count']['value']
            #total_hits = results["hits"]["total"]["value"]
            if total_hits > 0:
                # show number of results and time taken
                st.write(templates.number_of_results(total_hits, results['took'] / 1000),
                        unsafe_allow_html=True)
                # show popular tags
                if st.session_state.tags is not None and st.session_state.tags not in results['sorted_tags']:
                    popular_tags = [st.session_state.tags] + results['sorted_tags']
                else:
                    popular_tags = results['sorted_tags']

                # popular_tags_html = templates.tag_boxes(search,
                #                                         popular_tags[:10],
                #                                         st.session_state.tags)
                # st.write(popular_tags_html, unsafe_allow_html=True)
                # search results
                for i in range(len(results['hits']['hits'])):
                    res = utils.simplify_es_result(results['hits']['hits'][i])
                    st.write(templates.search_result(i + from_i, **res),
                            unsafe_allow_html=True)
                    # render tags
                    # tags_html = templates.tag_boxes(search, res['tags'],
                    #                                 st.session_state.tags)
                    # st.write(tags_html, unsafe_allow_html=True)

                # pagination
                if total_hits > page_size:
                    total_pages = (total_hits + page_size - 1) // page_size
                    pagination_html = templates.pagination(total_pages,
                                                        search_name,
                                                        search_address,
                                                        search_dob,
                                                        st.session_state.page,
                                                        st.session_state.tags,)
                    st.write(pagination_html, unsafe_allow_html=True)
            else:
                # no results found
                st.write(templates.no_result_html(), unsafe_allow_html=True)
