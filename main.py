"""Summarize heat-wave exposure against each location's own historic distribution."""
import argparse,json
from pathlib import Path
import pandas as pd
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--input",required=True);p.add_argument("--date",default="date");p.add_argument("--location",default="location");p.add_argument("--tmax",default="tmax_c");p.add_argument("--percentile",type=float,default=.95);p.add_argument("--out",default="outputs");a=p.parse_args()
 d=pd.read_csv(a.input);d[a.date]=pd.to_datetime(d[a.date],errors="coerce");d[a.tmax]=pd.to_numeric(d[a.tmax],errors="coerce");d=d.dropna(subset=[a.date,a.location,a.tmax]).sort_values(a.date)
 # The historical baseline is explicitly reported and should be fit only on a declared reference period in deployment.
 base=d.groupby(a.location)[a.tmax].quantile(a.percentile).rename("local_threshold");d=d.join(base,on=a.location);d["heat_day"]=d[a.tmax]>=d.local_threshold
 d["rolling_heat_days_3d"]=d.groupby(a.location).heat_day.transform(lambda s:s.astype(int).rolling(3,min_periods=1).sum())
 daily=d.groupby([a.location,d[a.date].dt.to_period("M")]).agg(days=("heat_day","sum"),max_tmax=(a.tmax,"max"),threshold=("local_threshold","first")).reset_index();daily["month"]=daily[a.date].astype(str);daily=daily.drop(columns=[a.date])
 out=Path(a.out);out.mkdir(parents=True,exist_ok=True);daily.to_csv(out/"monthly_heat_exposure.csv",index=False)
 report={"records":len(d),"locations":int(d[a.location].nunique()),"percentile":a.percentile,"heat_days":int(d.heat_day.sum()),"note":"Relative historical percentile is not a health-risk estimate; add humidity, vulnerability, and official warnings for response planning."}
 (out/"summary.json").write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=="__main__":main()
