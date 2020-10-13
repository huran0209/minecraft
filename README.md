# minecraft server
## server情報
- cpu: Xeon E3-1220 v6 @ 3.0GHz
- memory: DDR4-2400 (4GBを割当)
- storage: WD Blue 3D NAND SATA SSD

## world情報
- Game Mode: SURVIVAL  
- Difficulty: EASY  
- 毎日5:00にバックアップを実行

### world (初期ワールド)
- version: 1.14
- seed: 2744398826613602129

### resource_world(資源ワールド)
定期的にリセットする予定
- version: 1.14
- seed: -1389479166666961441

### nether_update
メインワールド追加
- version: 1.16

## plugins
- WorldEdit (https://dev.bukkit.org/projects/worldedit)  

- WorldBorder (https://www.spigotmc.org/resources/worldborder.60905/)  
メインワールドの大きさをr=4000に制限
```
/wb world set 4000 4000 0 0
/wb world fill
```

- Dynmap (https://dev.bukkit.org/projects/dynmap)
```
/dynmap fullrender world:flat
```

- Multiverse-Core (https://dev.bukkit.org/projects/multiverse-core)  
資源ワールドを追加

- Multiverse-Portals (https://dev.bukkit.org/projects/multiverse-portals)  
ワールド間移動用のポータル設置

- LunaChat (https://github.com/ucchyocean/LunaChat/releases)  
日本語チャット支援

- EditableSign (https://www.spigotmc.org/resources/editablesign.2502/)  
看板の編集を可能に

- UltimateTimber (https://songoda.com/marketplace/product/ultimatetimber-the-realistic-tree-chopper.18)  
木こり(*資源ワールドでのみ有効)
