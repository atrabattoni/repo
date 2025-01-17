import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from matplotlib.offsetbox import AnchoredText

from utils import bandpass

# event I
# case = "I"
# event = "20211003.042205"
# time = slice("2021-10-03T04:22:35.4", "2021-10-03T04:22:36.6")

# event II
# case = "II"
# event = "20210911.024800"
# time = slice("2021-09-11T02:48:29.6", "2021-09-11T02:48:30.8")

# # event III
case = "III"
event = "20210923.050400"
time = slice("2021-09-23T05:04:50", "2021-09-23T05:04:51")

# First arrival picking
offset = np.array([55, 121.6, 195.2])
delay = np.array([0.0, 0.215, 0.31])
t0 = 0.325
model = xr.DataArray(
    delay, coords={"offset": offset - offset.min()}, dims="offset")

xarr = xr.open_dataarray(f"../data/{event}.DAS.nc")
sampling_rate = 1 / xarr.attrs["dt"]
xarr = xr.apply_ufunc(bandpass, xarr, kwargs=dict(
    freqmin=1.0, freqmax=20.0, df=sampling_rate, axis=0), keep_attrs=True)

xarr = xarr.sel(
    time=time,
    offset=slice(0, 400),
)
xarr["time"] = (xarr["time"] - xarr["time"][0]) / np.timedelta64(1, "s")
xarr["time"] = xarr["time"] - t0


plt.style.use("figure.mplstyle")

mm = 1/25.4

fig, axes = plt.subplots(figsize=(95 * mm, 50 * mm),
                         dpi=300, constrained_layout=True)

ax = axes
vlim = 5e3
xarr.plot.imshow(ax=ax, norm=colors.SymLogNorm(linthresh=vlim/10, vmin=-vlim, vmax=vlim), yincrease=False,
                 cmap="viridis")
ax.axvline(51, color="black", lw=0.75)
ax.axvline(351, color="black", lw=0.75)
ax.plot(offset, delay, c="C3", lw=1, label="First arrival")
ax.set_ylim([0.8, -0.2])
ax.set_xlim([25, 375])
ax.legend(loc="lower right", framealpha=1.0, edgecolor="black")
ax.set_xlabel("Offset [m]")
ax.set_ylabel("Time [s]")
ax.annotate("A", (51, 1.01), xycoords=(
    "data", "axes fraction"), horizontalalignment="center")
ax.annotate("B", (351, 1.01), xycoords=(
    "data", "axes fraction"), horizontalalignment="center")
ax.images[-1].colorbar.set_label("Strain rate [nm/m/s]")
at = AnchoredText(
    case, frameon=True, loc='upper right', prop=dict(font="Times New Roman"))
at.patch.set_boxstyle("circle,pad=0.")
at.patch.set(facecolor="yellow")
ax.add_artist(at)

fig.savefig(f"fig6_{case}.png")
plt.close(fig)
