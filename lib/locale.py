from collections import OrderedDict

class Currency():
    TYPES = OrderedDict([
        ('usd', u'United States Dollar'),
        ('aed', u'United Arab Emirates Dirham'),
        ('afn', u'Afghan Afghani'),
        ('all', u'Albanian Lek'),
        ('amd', u'Armenian Dram'),
        ('ang', u'Netherlands Antillean Gulden'),
        ('aoa', u'Angolan Kwanza'),
        ('ars', u'Argentine Peso'),
        ('aud', u'Australian Dollar'),
        ('awg', u'Aruban Florin'),
        ('azn', u'Azerbaijani Manat'),
        ('bam', u'Bosnia & Herzegovina Convertible Mark'),
        ('bbd', u'Barbadian Dollar'),
        ('bdt', u'Bangladeshi Taka'),
        ('bgn', u'Bulgarian Lev'),
        ('bif', u'Burundian Franc'),
        ('bmd', u'Bermudian Dollar'),
        ('bnd', u'Brunei Dollar'),
        ('bob', u'Bolivian Boliviano'),
        ('brl', u'Brazilian Real'),
        ('bsd', u'Bahamian Dollar'),
        ('bwp', u'Botswana Pula'),
        ('bzd', u'Belize Dollar'),
        ('cad', u'Canadian Dollar'),
        ('cdf', u'Congolese Franc'),
        ('chf', u'Swiss Franc'),
        ('clp', u'Chilean Peso'),
        ('cny', u'Chinese Renminbi Yuan'),
        ('cop', u'Colombian Peso'),
        ('crc', u'Costa Rican Colón'),
        ('cve', u'Cape Verdean Escudo'),
        ('czk', u'Czech Koruna'),
        ('djf', u'Djiboutian Franc'),
        ('dkk', u'Danish Krone'),
        ('dop', u'Dominican Peso'),
        ('dzd', u'Algerian Dinar'),
        ('eek', u'Estonian Kroon'),
        ('egp', u'Egyptian Pound'),
        ('etb', u'Ethiopian Birr'),
        ('eur', u'Euro'),
        ('fjd', u'Fijian Dollar'),
        ('fkp', u'Falkland Islands Pound'),
        ('gbp', u'British Pound'),
        ('gel', u'Georgian Lari'),
        ('gip', u'Gibraltar Pound'),
        ('gmd', u'Gambian Dalasi'),
        ('gnf', u'Guinean Franc'),
        ('gtq', u'Guatemalan Quetzal'),
        ('gyd', u'Guyanese Dollar'),
        ('hkd', u'Hong Kong Dollar'),
        ('hnl', u'Honduran Lempira'),
        ('hrk', u'Croatian Kuna'),
        ('htg', u'Haitian Gourde'),
        ('huf', u'Hungarian Forint'),
        ('idr', u'Indonesian Rupiah'),
        ('ils', u'Israeli New Sheqel'),
        ('inr', u'Indian Rupee'),
        ('isk', u'Icelandic Króna'),
        ('jmd', u'Jamaican Dollar'),
        ('jpy', u'Japanese Yen'),
        ('kes', u'Kenyan Shilling'),
        ('kgs', u'Kyrgyzstani Som'),
        ('khr', u'Cambodian Riel'),
        ('kmf', u'Comorian Franc'),
        ('krw', u'South Korean Won'),
        ('kyd', u'Cayman Islands Dollar'),
        ('kzt', u'Kazakhstani Tenge'),
        ('lak', u'Lao Kip'),
        ('lbp', u'Lebanese Pound'),
        ('lkr', u'Sri Lankan Rupee'),
        ('lrd', u'Liberian Dollar'),
        ('lsl', u'Lesotho Loti'),
        ('ltl', u'Lithuanian Litas'),
        ('lvl', u'Latvian Lats'),
        ('mad', u'Moroccan Dirham'),
        ('mdl', u'Moldovan Leu'),
        ('mga', u'Malagasy Ariary'),
        ('mkd', u'Macedonian Denar'),
        ('mnt', u'Mongolian Tögrög'),
        ('mop', u'Macanese Pataca'),
        ('mro', u'Mauritanian Ouguiya'),
        ('mur', u'Mauritian Rupee'),
        ('mvr', u'Maldivian Rufiyaa'),
        ('mwk', u'Malawian Kwacha'),
        ('mxn', u'Mexican Peso'),
        ('myr', u'Malaysian Ringgit'),
        ('mzn', u'Mozambican Metical'),
        ('nad', u'Namibian Dollar'),
        ('ngn', u'Nigerian Naira'),
        ('nio', u'Nicaraguan Córdoba'),
        ('nok', u'Norwegian Krone'),
        ('npr', u'Nepalese Rupee'),
        ('nzd', u'New Zealand Dollar'),
        ('pab', u'Panamanian Balboa'),
        ('pen', u'Peruvian Nuevo Sol'),
        ('pgk', u'Papua New Guinean Kina'),
        ('php', u'Philippine Peso'),
        ('pkr', u'Pakistani Rupee'),
        ('pln', u'Polish Złoty'),
        ('pyg', u'Paraguayan Guaraní'),
        ('qar', u'Qatari Riyal'),
        ('ron', u'Romanian Leu'),
        ('rsd', u'Serbian Dinar'),
        ('rub', u'Russian Ruble'),
        ('rwf', u'Rwandan Franc'),
        ('sar', u'Saudi Riyal'),
        ('sbd', u'Solomon Islands Dollar'),
        ('scr', u'Seychellois Rupee'),
        ('sek', u'Swedish Krona'),
        ('sgd', u'Singapore Dollar'),
        ('shp', u'Saint Helenian Pound'),
        ('sll', u'Sierra Leonean Leone'),
        ('sos', u'Somali Shilling'),
        ('srd', u'Surinamese Dollar'),
        ('std', u'São Tomé and Príncipe Dobra'),
        ('svc', u'Salvadoran Colón'),
        ('szl', u'Swazi Lilangeni'),
        ('thb', u'Thai Baht'),
        ('tjs', u'Tajikistani Somoni'),
        ('top', u'Tongan Paʻanga'),
        ('try', u'Turkish Lira'),
        ('ttd', u'Trinidad and Tobago Dollar'),
        ('twd', u'New Taiwan Dollar'),
        ('tzs', u'Tanzanian Shilling'),
        ('uah', u'Ukrainian Hryvnia'),
        ('ugx', u'Ugandan Shilling'),
        ('uyu', u'Uruguayan Peso'),
        ('uzs', u'Uzbekistani Som'),
        ('vef', u'Venezuelan Bolívar'),
        ('vnd', u'Vietnamese Đồng'),
        ('vuv', u'Vanuatu Vatu'),
        ('wst', u'Samoan Tala'),
        ('xaf', u'Central African Cfa Franc'),
        ('xcd', u'East Caribbean Dollar'),
        ('xof', u'West African Cfa Franc'),
        ('xpf', u'Cfp Franc'),
        ('yer', u'Yemeni Rial'),
        ('zar', u'South African Rand'),
        ('zmw', u'Zambian Kwacha')
    ])

    @classmethod
    def lookup(cls, currency_code):
        """
        Return the full currency name.

        :param currency_code: Currency abbreviation
        :type currency_code: str
        :return: str
        """
        return Currency.TYPES[currency_code]