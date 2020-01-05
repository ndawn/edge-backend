--
-- Data for Name: commerce_category; Type: TABLE DATA; Schema: public; Owner: www
--

COPY public.commerce_category (id, title, description, slug, background, parent_id) FROM stdin;
1	Комиксы		comics	\N	\N
2	Синглы		singles	\N	1
3	Сборники		tpbs	\N	1
4	Фигурки		figurines	\N	\N
\.


--
-- Data for Name: commerce_pricemap; Type: TABLE DATA; Schema: public; Owner: www
--

COPY public.commerce_pricemap (id, mode, usd, bought, "default", discount, superior, weight) FROM stdin;
2	monthly	2.99000000000000021	167.400000000000006	400	290	230	100
3	monthly	3.99000000000000021	203.400000000000006	450	350	290	100
4	monthly	4.69000000000000039	228.599999999999994	500	390	330	100
5	monthly	5.99000000000000021	275.399999999999977	550	450	390	100
6	monthly	6.99000000000000021	311.399999999999977	600	490	430	100
16	monthly	4.99000000000000021	239.400000000000006	500	390	330	100
25	weekly	106.25	5611	8000	6999	0	3000
44	weekly	84.9899999999999949	4340	7000	5699	0	3000
45	weekly	21.25	1380	1800	1599	0	100
46	weekly	25.5	1643	2000	1839	0	100
49	weekly	5.95000000000000018	431	650	549	0	100
50	weekly	29.75	1907	2500	2099	0	100
52	weekly	33.990000000000002	1736	2600	2399	0	1900
53	weekly	42.490000000000002	2046	3500	2899	0	1900
55	weekly	29.7399999999999984	1457	2200	1999	0	1900
57	weekly	42.5	2046	3500	2899	0	1900
58	weekly	25.4899999999999984	1277	1900	1799	0	1500
60	weekly	63.75	2895	5000	3899	0	2000
62	weekly	85	4340	7000	5699	0	3000
63	weekly	21.2399999999999984	1097	1700	1499	0	1000
0	\N	0	0	0	0	0	100
18	monthly	34.990000000000002	1457	2200	1890	34.990000000000002	1900
30	weekly	5.08999999999999986	430	615	555	0	100
51	weekly	5.94000000000000039	492	635	705	0	100
31	weekly	6.79000000000000004	554	790	715	0	100
32	weekly	8.49000000000000021	678	975	875	0	200
56	weekly	8.5	679	975	875	0	100
7	monthly	9.99000000000000021	483	800	650	695	700
9	monthly	12.9900000000000002	576	1100	790	875	700
10	monthly	14.9900000000000002	663	1250	850	965	700
11	monthly	15.9900000000000002	694	1300	890	995	700
21	monthly	39.990000000000002	1736	2899	2499	39.990000000000002	1900
12	monthly	16.9899999999999984	750	1300	990	1065	700
13	monthly	17.9899999999999984	806	1400	1090	1135	700
14	monthly	19.9899999999999984	942	1600	1290	1235	700
15	monthly	24.9899999999999984	1097	1700	1390	24.9899999999999984	1000
17	monthly	29.9899999999999984	1277	1900	1690	34.990000000000002	1500
22	monthly	49.990000000000002	2046	3500	2999	49.990000000000002	1900
23	monthly	50	2046	3500	2999	50	1900
8	monthly	75	2895	5000	3690	75	2000
19	monthly	99.9899999999999949	4340	7000	5490	99.9899999999999949	3000
20	monthly	100	4340	7000	5999	100	3000
24	monthly	125	5611	8000	6999	125	3000
1	monthly	1	102	165	160	145	100
26	weekly	1	120	230	195	0	100
27	weekly	2.54000000000000004	244	344	315	0	100
37	weekly	2.99000000000000021	304	400	365	0	100
28	weekly	3.39000000000000012	306	435	395	0	100
43	weekly	3.99000000000000021	349	500	449	0	100
29	weekly	4.24000000000000021	368	525	475	0	100
47	weekly	4.25	368	525	475	0	100
34	weekly	10	682	1000	10	0	100
61	weekly	10.1999999999999993	694	1000	10.1999999999999993	0	100
35	weekly	11.0399999999999991	576	1100	11.0399999999999991	0	700
36	weekly	12	806	1300	12	0	100
54	weekly	12.7400000000000002	663	1250	12.7400000000000002	0	700
33	weekly	12.75	853	1300	12.75	0	100
59	weekly	13.5899999999999999	694	1300	13.5899999999999999	0	700
38	weekly	14.4399999999999995	750	1300	14.4399999999999995	0	700
48	weekly	15.2899999999999991	806	1400	15.2899999999999991	0	700
39	weekly	15.3000000000000007	1011	15.3000000000000007	15.3000000000000007	0	100
40	weekly	16.9899999999999984	942	1600	16.9899999999999984	0	700
41	weekly	17	1116	1500	17	0	100
42	weekly	18	1178	1600	18	0	100
\.


--
-- Data for Name: commerce_publisher; Type: TABLE DATA; Schema: public; Owner: www
--

COPY public.commerce_publisher (id, full_name, short_name) FROM stdin;
1	Marvel Comics	Marvel
2	DC Comics	DC
3	Image Comics	Image
4	IDW Publishing	IDW
5	Dark Horse Comics	Dark Horse
\.


--
-- Data for Name: previews_categorydata; Type: TABLE DATA; Schema: public; Owner: www
--

COPY public.previews_categorydata (id, identifier, name, "default", category_id, site_id) FROM stdin;
1	1	Comics	t	2	1
2	3	Graphic Novels/Trade Paperbacks	t	3	1
\.


--
-- Data for Name: previews_publisherdata; Type: TABLE DATA; Schema: public; Owner: www
--

COPY public.previews_publisherdata (id, full_name, short_name, singles_category_code, tp_category_code, "default", publisher_id, site_id) FROM stdin;
1	MARVEL COMICS	MARVEL	1	3	t	1	1
2	DC COMICS	DC	1	3	t	2	1
3	IMAGE COMICS	IMAGE	1	3	t	3	1
4	IDW PUBLISHING	IDW	1	3	t	4	1
5	DARK HORSE COMICS	DH	1	3	f	5	1
\.


--
-- Name: commerce_category_id_seq; Type: SEQUENCE SET; Schema: public; Owner: www
--

SELECT pg_catalog.setval('public.commerce_category_id_seq', 4, true);


--
-- Name: commerce_pricemap_id_seq; Type: SEQUENCE SET; Schema: public; Owner: www
--

SELECT pg_catalog.setval('public.commerce_pricemap_id_seq', 64, true);


--
-- Name: commerce_publisher_id_seq; Type: SEQUENCE SET; Schema: public; Owner: www
--

SELECT pg_catalog.setval('public.commerce_publisher_id_seq', 5, true);


--
-- Name: previews_categorydata_id_seq; Type: SEQUENCE SET; Schema: public; Owner: www
--

SELECT pg_catalog.setval('public.previews_categorydata_id_seq', 2, true);


--
-- Name: previews_publisherdata_id_seq; Type: SEQUENCE SET; Schema: public; Owner: www
--

SELECT pg_catalog.setval('public.previews_publisherdata_id_seq', 5, true);
