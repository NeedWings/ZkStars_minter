RPC_LIST = {
    "scroll"    : ["https://rpc.scroll.io"],
    "zksync"    : ["https://zksync_era.public-rpc.com"],
    "zora"      : ["https://rpc.zora.energy"],
    "linea"     : ["https://1rpc.io/linea"],
    "base"      : ["https://base.llamarpc.com"],
}

ErrorSleepeng = [1, 2] #В секундах. Сколько ждать при ошибке
TaskSleep = [1, 2] #В секундах. Сколько ждать после выполнения задачи

mintAmount = [1, 2] # сколько нфт минтить

NET = "scroll" # в какой сети минтить

ref = "0x739815d56A5FFc21950271199D2cf9E23B944F1c" # реф. По стандарту стоит тот же, что и на сайте

advanced_mint_mode = False # Если True, то не будет минтить уже сминченные нфт