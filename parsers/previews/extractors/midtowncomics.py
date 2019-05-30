from parsers.previews.extractors import ItemExtractor, VariantExtractor, PreviewExtractor


class MidtowncomicsItemExtractor(ItemExtractor):
    def get_title(self):
        pass

    def get_origin_title(self):
        pass

    def get_description(self):
        pass

    def get_category(self):
        pass

    def get_publisher(self):
        pass


class MitdowncomicsVariantExtractor(VariantExtractor):
    def get_title(self):
        pass

    def get_origin_title(self):
        pass

    def get_bought(self):
        pass

    def get_price_map(self):
        pass

    def get_price(self):
        pass

    def get_weight(self):
        pass

    def get_cover(self):
        pass


class MidtowncomicsPreviewExtractor(PreviewExtractor):
    def get_mode(self):
        return 'weekly'

    def get_origin_url(self):
        return self.tree.url

    def get_price_map(self):
        pass

    def get_release_date(self):
        pass

    def get_midtown_id(self):
        pass
