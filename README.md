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

5. In Seeq Workbench retrieve the checksum of the newly created Clustering.py external calc call. Wait a few moments for it to update, then in your Clustering SDL, open an SDL terminal and navigate to `clustering` directory:

```bash
> cd /seeq/addons/clustering/
```

6. Run the following command to update your instance of clustering to point to your instance of the external calc script:

```bash
> python config checksum <yourchecksumhere>
```
## Install add on tool

7. Ensure that add on tools are enabled in your version of Seeq. For instructions on how to do this, see 
here(https://seeq.atlassian.net/wiki/spaces/KB/pages/961675391/Add-on+Tool+Administration+and+Development#Add-on-Tools-appear-in-an-%E2%80%9CAdd-ons%E2%80%9D-group-on-the-Seeq-Tools-panel.-These-tools-typically-open-an-appmode-SDL-notebook)

8. Note the URL of your Seeq Server instance, then run the following command in SDL terminal

```bash
python _install_addon.py --username <username> --password <password> --seeq_url <seeq_server_url>
```

	a. Options on install:
