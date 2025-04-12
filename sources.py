from models import Source

Morpho = [
    Source(lending='morpho', chain='mainnet', name='wbtc_usdc', url='https://app.morpho.org/market?id=0x3a85e619751152991742810df6ec69ce473daef99e28a64ab2340d7b7ccfee49&network=mainnet'),
    Source(lending='morpho', chain='base', name='weth_usdc', url='https://app.morpho.org/market?id=0x8793cf302b8ffd655ab97bd1c695dbd967807e8367a65cb2f4edaf1380ba1bda&network=base'),
    Source(lending='morpho', chain='base', name='cbeth_usdc', url='https://app.morpho.org/market?id=0x1c21c59df9db44bf6f645d854ee710a8ca17b479451447e9f56758aee10a2fad&network=base'),
    Source(lending='morpho', chain='base', name='cbbtc_usdc', url='https://app.morpho.org/market?id=0x9103c3b4e834476c9a62ea009ba2c884ee42e94e6e314a26f04d312434191836&network=base'),
    Source(lending='morpho', chain='base', name='wsteth_usdc', url='https://app.morpho.org/market?id=0x13c42741a359ac4a8aa8287d2be109dcf28344484f91185f9a79bd5a805a55ae&network=base'),
]


Aave = [
    Source(lending='aave', chain='mainnet', name='usdc', url='https://app.aave.com/reserve-overview/?underlyingAsset=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48&marketName=proto_mainnet_v3'),
    Source(lending='aave', chain='mainnet', name='usdt', url='https://app.aave.com/reserve-overview/?underlyingAsset=0xdac17f958d2ee523a2206206994597c13d831ec7&marketName=proto_mainnet_v3'),
    Source(lending='aave', chain='arbitrum', name='usdc', url='https://app.aave.com/reserve-overview/?underlyingAsset=0xaf88d065e77c8cc2239327c5edb3a432268e5831&marketName=proto_arbitrum_v3'),
    Source(lending='aave', chain='arbitrum', name='usdt', url='https://app.aave.com/reserve-overview/?underlyingAsset=0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9&marketName=proto_arbitrum_v3'),
    Source(lending='aave', chain='base', name='usdc', url='https://app.aave.com/reserve-overview/?underlyingAsset=0x833589fcd6edb6e08f4c7c32d4f71b54bda02913&marketName=proto_base_v3'),
]


Fluid = [
    Source(lending='fluid', chain='mainnet', name='weth_usdc', url='https://fluid.instadapp.io/stats/1/vaults#11'),
    Source(lending='fluid', chain='mainnet', name='weth_usdt', url='https://fluid.instadapp.io/stats/1/vaults#12'),
    Source(lending='fluid', chain='mainnet', name='wsteth_usdc', url='https://fluid.instadapp.io/stats/1/vaults#14'),
    Source(lending='fluid', chain='mainnet', name='wsteth_usdt', url='https://fluid.instadapp.io/stats/1/vaults#15'),
    Source(lending='fluid', chain='arbitrum', name='weth_usdc', url='https://fluid.instadapp.io/stats/42161/vaults#1'),
    Source(lending='fluid', chain='base', name='weth_usdc', url='https://fluid.instadapp.io/stats/8453/vaults#1'),
]


Compound = [
    Source(lending='compound', chain='mainnet', name='usdc', url='https://app.compound.finance/markets/usdc-mainnet'),
]
