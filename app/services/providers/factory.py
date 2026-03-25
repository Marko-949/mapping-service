from .woo_provider import WooCommerceProvider

class ProviderFactory:
    @staticmethod
    def get_provider(provider_type: str, credentials: dict):
        provider_type = provider_type.lower()
        
        if provider_type == "woocommerce":
            return WooCommerceProvider(
                base_url=credentials.get("url"),
                ck=credentials.get("ck"),
                cs=credentials.get("cs")
            )
        
        # elif provider_type == "shopify":
        #     return ShopifyProvider(token=credentials.get("token"))
            
        else:
            raise ValueError(f"Provajder '{provider_type}' trenutno nije podržan.")