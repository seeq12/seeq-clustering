# Clustering

## External Calc Installation and Configuration:

1. Clone this repo to Seeq Data Lab
2. Move two files `./seeq/addons/clustering/Clustering.py` and `/seeq/addons/clustering/Clustering_config.py` to the external calculation folder (typically `'D:/Seeq/plugins/external-calculation/python/user/'` or similar)

**Ensure the next 4 steps are done in the correct order**

3. In command line on the computer or server running Seeq, navigate to the external calculation python folder (using the example from above):
```bash
> cd D:/Seeq/plugins/external-calculation/python/user/
```
4. Configure the local location where clustering models will be stored:

```bash
> python Clustering_config clusteringModelsPath
```

You may also wish to store them somewhere you specify. This can be done as:

```bash
> python Clustering_config clusteringModelsPath <yourpathhere>
```

5. In Seeq retrieve the checksum of the newly created Clustering.py external calc call. Wait a few moments for it to update, then in an SDL terminal navigate to `clustering` directory:

```bash
> cd /seeq/addons/clustering/
```

6. Run the following command to update your instance of clustering to point to your instance of the external calc script:

```bash
> python config checksum <yourchecksumhere>
```

