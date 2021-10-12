# Features that work

`get_judge_vis` that lives in the `visualizations.py` file is the working function that is currently being used to display the graphs on the deployed site.

`/vis/judge/{judge_id}` is the endpoint of the `get_judge_vis` function and it can be found inside of the `main.py` file.


# Features that need work

`get_judge_feature_vis` is what should be worked on next to obtain a more robust visualization. `get_judge_feature_vis` can also be found in the `visualizations.py` file.

`/vis/judge/{judge_id}/{feature}` is the endpoint of the `get_judge_feature_vis` function and it can be found inside of the `main.py` file.

The `get_judge_feature_vis` should be working but has not been tested yet. It will require a new endpoint to be made by the web team.

`get_judge_feature_vis` IS THE REPLACEMENT FOR `get_judge_vis` that is currently working deployed.

Please note that the only reason for the `get_judge_feature_vis` function, is to improve the visualizations. It will allow for many different features to be compared opposed to the comparison of just outcome by protected grounds.

As stated before, `get_judge_feature_vis` should be fully functioning but will require a new endpoint to be made by the web team, this will be very similar to the one that is already made other than needing thee option for a drop down tab.

Please see the loom and trello below for more info.

### Important Note

Both of these functions are commented out because they have been replaced by the ones above.

IF EITHER `get_judge_vis` OR `get_judge_vis` ARE DEPLOYED AND WORKING DELETE THE COMMENTED OUT CODE. 

The `get_judge_side_bar()` function that is contained in the visualizations.py is no longer working and is a reference in case the other functions don't deploy correctly. 

The endpoint for the old, `get_judge_side_bar()` looks like `/vis/outcome-by-judge/{judge_name}` and can be found at the very bottom of the `main.py` file.

# \/ VALUABLE \/
[Trello Card](https://trello.com/c/qAuXVBzy/3-data-viz-connect-ds-data-viz-to-be-fes-endpoint)
[Loom Video](https://www.loom.com/share/454f794c52c94e5b81e33770d3d44ad3)