

# 研究目的

本專題以 **foamMooring** 工具箱為基礎，模擬單一矩形浮體（floating body）在不同波浪條件下的運動響應。
藉由系統性地改變波浪週期與波高，分析浮體在三自由度運動（3-DoF） 下的 **RAO（Response Amplitude Operator）**
特性，了解浮體對波浪頻率的動態反應，並探討共振現象與繫泊系統的影響。

研究結果可作為：

1.  浮體動力行為的初步驗證；
2.  對照不同繫泊剛度或幾何設定的參考；
3.  後續延伸研究（例如多浮體干涉、風浪耦合等）的基礎資料。


# 模擬條件概述

根據 Chen and Hall (2022) 的單一浮體案例，本研究採用相同的幾何、繫泊與水槽條件，改變波浪週期與波高兩個主要參數。


## 浮體條件

-   浮體長度 $2b = 0.2~\mathrm{m}$
-   浮體寬度 $0.2~\mathrm{m}$
-   浮體高度 $0.132~\mathrm{m}$
-   初始吃水深度 $d = 0.0786~\mathrm{m}$
-   浮體質量 $3.16~\mathrm{kg}$
-   質量中心 $(x, y, z) = (0, 0, -0.0126)~\mathrm{m}$
-   浮體慣性矩 (I<sub>xx</sub>, I<sub>yy</sub>, I<sub>zz</sub>) = $(0.015, 0.015, 0.021)~\mathrm{kg\, m^2}$
-   靜止水深 $h = 0.5~\mathrm{m}$


## 繫泊條件

-   繫纜單位長度質量 $0.607~\mathrm{g/cm} = 0.0607~\mathrm{kg/m}$
-   繫纜直徑 $0.003656~\mathrm{m}$
-   繫纜長度 $1.455~\mathrm{m}$
-   繫纜軸向剛度 (axial stiffness) $29~\mathrm{N}$
-   繫纜導纜器 (fairlead, 與浮體連接處) $(x, y, z) = (\pm 0.1, \pm 0.1, -0.0736)~\mathrm{m}$
-   繫纜錨定處 (ahcnor, 與底床連接處) $(x, y, z) = (\pm 1.385, \pm 0.423, -0.5)~\mathrm{m}$


## Chen and Hall (2022) 之波浪條件

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-right" />

<col  class="org-right" />

<col  class="org-right" />

<col  class="org-right" />

<col  class="org-right" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">編號</th>
<th scope="col" class="org-right">週期 \(T\) (s)</th>
<th scope="col" class="org-right">波高 \(H\) (m)</th>
<th scope="col" class="org-right">波長 \(L\) (m)</th>
<th scope="col" class="org-right">波尖銳度 \(H/L\)</th>
<th scope="col" class="org-right">相對水深 \(h/L\)</th>
</tr>
</thead>

<tbody>
<tr>
<td class="org-left">H12T18</td>
<td class="org-right">1.8</td>
<td class="org-right">0.12</td>
<td class="org-right">3.57</td>
<td class="org-right">0.0336</td>
<td class="org-right">0.140</td>
</tr>


<tr>
<td class="org-left">H12T20</td>
<td class="org-right">2.0</td>
<td class="org-right">0.12</td>
<td class="org-right">4.06</td>
<td class="org-right">0.0296</td>
<td class="org-right">0.123</td>
</tr>


<tr>
<td class="org-left">H15T18</td>
<td class="org-right">1.8</td>
<td class="org-right">0.15</td>
<td class="org-right">3.57</td>
<td class="org-right">0.0420</td>
<td class="org-right">0.140</td>
</tr>
</tbody>
</table>

以相對水深 $(h/L)$ 來分類，以上波浪均屬中間水深波 (intermediate water waves)。波浪尖銳度 (wave steepness) $H/L$ 與波浪的非線性程度有關，但並非一個獨立的分類指標。相對水深之分類為：

-   深水波: $h/L > 1/2$
-   中間水深波: $1/20 < h/L < 1/2$
-   淺水波: $h/L < 1/20$


# 計算條件設定

靜水深 $h = 0.5~\mathrm{m}$, 浮體半寬 $b = 0.1~\mathrm{m}$。
以波數 (wave number) $k = 2\pi/L$ 之倒數為長度之無因次尺度，其中 $L$ 為波長。改變波浪週期 $T$ 可得到不同之 $k$ 值。

規劃相對之浮體寬為 $kb = 0.3 \sim 1.2$, 波浪尖銳度 $ka = 0.05, 0.1$, 其中 $a = H/2$ 為入射波振幅。
計算例設定如下表：

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-right" />

<col  class="org-right" />

<col  class="org-right" />

<col  class="org-right" />

<col  class="org-right" />

<col  class="org-right" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-right">No.</th>
<th scope="col" class="org-right">kb</th>
<th scope="col" class="org-right">ka</th>
<th scope="col" class="org-right">H (m)</th>
<th scope="col" class="org-right">L (m)</th>
<th scope="col" class="org-right">T (s)</th>
</tr>
</thead>

<tbody>
<tr>
<td class="org-right">1</td>
<td class="org-right">0.30</td>
<td class="org-right">0.05</td>
<td class="org-right">0.0333</td>
<td class="org-right">2.0944</td>
<td class="org-right">1.217</td>
</tr>


<tr>
<td class="org-right">2</td>
<td class="org-right">0.40</td>
<td class="org-right">0.05</td>
<td class="org-right">0.0250</td>
<td class="org-right">1.5708</td>
<td class="org-right">1.022</td>
</tr>


<tr>
<td class="org-right">3</td>
<td class="org-right">0.50</td>
<td class="org-right">0.05</td>
<td class="org-right">0.0200</td>
<td class="org-right">1.2566</td>
<td class="org-right">0.903</td>
</tr>


<tr>
<td class="org-right">4</td>
<td class="org-right">0.60</td>
<td class="org-right">0.05</td>
<td class="org-right">0.0167</td>
<td class="org-right">1.0472</td>
<td class="org-right">0.821</td>
</tr>


<tr>
<td class="org-right">5</td>
<td class="org-right">0.70</td>
<td class="org-right">0.05</td>
<td class="org-right">0.0143</td>
<td class="org-right">0.8976</td>
<td class="org-right">0.759</td>
</tr>


<tr>
<td class="org-right">6</td>
<td class="org-right">0.80</td>
<td class="org-right">0.05</td>
<td class="org-right">0.0125</td>
<td class="org-right">0.7854</td>
<td class="org-right">0.709</td>
</tr>


<tr>
<td class="org-right">7</td>
<td class="org-right">0.90</td>
<td class="org-right">0.05</td>
<td class="org-right">0.0111</td>
<td class="org-right">0.6981</td>
<td class="org-right">0.669</td>
</tr>


<tr>
<td class="org-right">8</td>
<td class="org-right">1.00</td>
<td class="org-right">0.05</td>
<td class="org-right">0.0100</td>
<td class="org-right">0.6283</td>
<td class="org-right">0.634</td>
</tr>


<tr>
<td class="org-right">9</td>
<td class="org-right">1.10</td>
<td class="org-right">0.05</td>
<td class="org-right">0.0091</td>
<td class="org-right">0.5712</td>
<td class="org-right">0.605</td>
</tr>


<tr>
<td class="org-right">10</td>
<td class="org-right">1.20</td>
<td class="org-right">0.05</td>
<td class="org-right">0.0083</td>
<td class="org-right">0.5236</td>
<td class="org-right">0.579</td>
</tr>


<tr>
<td class="org-right">11</td>
<td class="org-right">0.30</td>
<td class="org-right">0.10</td>
<td class="org-right">0.0667</td>
<td class="org-right">2.0944</td>
<td class="org-right">1.217</td>
</tr>


<tr>
<td class="org-right">12</td>
<td class="org-right">0.40</td>
<td class="org-right">0.10</td>
<td class="org-right">0.0500</td>
<td class="org-right">1.5708</td>
<td class="org-right">1.022</td>
</tr>


<tr>
<td class="org-right">13</td>
<td class="org-right">0.50</td>
<td class="org-right">0.10</td>
<td class="org-right">0.0400</td>
<td class="org-right">1.2566</td>
<td class="org-right">0.903</td>
</tr>


<tr>
<td class="org-right">14</td>
<td class="org-right">0.60</td>
<td class="org-right">0.10</td>
<td class="org-right">0.0333</td>
<td class="org-right">1.0472</td>
<td class="org-right">0.821</td>
</tr>


<tr>
<td class="org-right">15</td>
<td class="org-right">0.70</td>
<td class="org-right">0.10</td>
<td class="org-right">0.0286</td>
<td class="org-right">0.8976</td>
<td class="org-right">0.759</td>
</tr>


<tr>
<td class="org-right">16</td>
<td class="org-right">0.80</td>
<td class="org-right">0.10</td>
<td class="org-right">0.0250</td>
<td class="org-right">0.7854</td>
<td class="org-right">0.709</td>
</tr>


<tr>
<td class="org-right">17</td>
<td class="org-right">0.90</td>
<td class="org-right">0.10</td>
<td class="org-right">0.0222</td>
<td class="org-right">0.6981</td>
<td class="org-right">0.669</td>
</tr>


<tr>
<td class="org-right">18</td>
<td class="org-right">1.00</td>
<td class="org-right">0.10</td>
<td class="org-right">0.0200</td>
<td class="org-right">0.6283</td>
<td class="org-right">0.634</td>
</tr>


<tr>
<td class="org-right">19</td>
<td class="org-right">1.10</td>
<td class="org-right">0.10</td>
<td class="org-right">0.0182</td>
<td class="org-right">0.5712</td>
<td class="org-right">0.605</td>
</tr>


<tr>
<td class="org-right">20</td>
<td class="org-right">1.20</td>
<td class="org-right">0.10</td>
<td class="org-right">0.0167</td>
<td class="org-right">0.5236</td>
<td class="org-right">0.579</td>
</tr>
</tbody>
</table>


# 參數意義與物理說明


## 波浪週期 $T~(\mathrm{s})$

波浪週期為相鄰波峰通過同一點所需的時間，決定波浪頻率與能量分佈。

-   短週期波 ($T < 1.4~\mathrm{s}$): 波浪變化快，主要影響 **surge** 運動；
-   長週期波 ($T > 1.6~\mathrm{s}$): 波浪能量集中，容易引發浮體共振。


## 波高 $H~(\mathrm{m})$

波高為波峰與波谷之間的垂直距離，反映波能強度。波高越大，浮體受力與運動幅度越明顯。

-   小波高：系統近似線性，可用於驗證理論模型。
-   大波高：可能產生非線性效應，例如阻尼增加或漂移運動。


## 波長 $L~(\mathrm{m})$

波長代表波峰與波峰之間的水平距離，與週期相關，由頻散關係：

$$
\omega^2 = g k \tanh (kh)
$$

可求得 $L = 2\pi / k$。
波長越長，波浪越「平緩」，對浮體的影響主要為低頻大振幅運動。


## 波陡度 $H/L$

波陡度描述波浪的相對「尖銳程度」，在水力學上常用來判斷波浪是否可能破碎。
一般而言：

-   $H/L < 0.02$ 為「緩波」；
-   $0.02 < H/L < 0.05$ 為「中等波」；
-   $H/L > 0.05$ 則為「陡波」區域，數值模擬需特別注意穩定性。


## 水深 $h~(\mathrm{m})$

水深影響波的傳播速度與波壓分佈。若 $kh > \pi$ 為深水波；若 $kh < \pi/10$ 為淺水波。
本研究之 $h = 0.6~\mathrm{m}$，屬於中等深度（intermediate depth），適合觀察深水與淺水效應交替之情況。


# 實驗步驟建議

1.  先選定基準案例（T = 1.8 s, H = 0.12 m），確認模擬可正常收斂；
2.  再依序執行各週期的掃描；
3.  模擬完成後，取浮體 3DoF 運動時間序列；
4.  計算各自由度的 RAO（振幅比與相位差）;
5.  繪製 RAO vs. 週期圖，觀察共振行為；
6.  彙整結果，分析波浪頻率與振幅對浮體動態特性的影響。


# 分析與討論方向

-   不同波陡度對浮體運動的非線性效應；
-   短波與長波下的共振頻率差異；
-   吃水深度與繫泊剛度對 RAO 峰值的影響；
-   CFD 模擬與理論模型的比較（例如 Morison 方程或線性勢流理論）。


# 學習重點

-   理解浮體受波激勵運動的機制；
-   熟悉 OpenFOAM 與 foamMooring 的模擬流程；
-   學習如何設計與執行參數掃描；
-   具備後處理分析（RAO 計算、頻譜分析）的能力；
-   建立對海洋結構物動力行為的直觀理解。


# 延伸方向

完成本階段後，可考慮進一步主題：

1.  探討繫泊剛度對 RAO 曲線的變化；
2.  研究多浮體間的水動力干涉；
3.  考慮風浪同時作用（加入定常風載）；
4.  嘗試使用不同繫泊模型（MoorDyn vs MAP++）比較。


# Overset 計算執行


## 計算指令

在案例主目錄中執行 `./Allrun.pre`, 可執行平行計算。如需進行單核心計算，則將其修改為

    #!/bin/sh
    cd "${0%/*}" || exit                                # Run from this directory
    . ${WM_PROJECT_DIR:?}/bin/tools/RunFunctions        # Tutorial run functions
    #------------------------------------------------------------------------------
    
    # Mesh floating body
    (cd floatingBody && ./Allrun.pre)
    
    ## Add background mesh (Parallel computing)
    #(cd background  && ./Allrun.pre 1)
    
    # Add background mesh (Single-Core computing)
    (cd background  && ./Allrun.pre)
    
    #------------------------------------------------------------------------------


## 平行計算設定

以 `tutorials/overset_parallel/` 為例：


## 計算分割數

設定為 4 區，可於 `background/system/decomposeParDict` 中設定。


# Overset 網格計算與後處理


## ParaView 繪圖


### 波浪流場與物體繪製流程

1.  開啟 `aa.foam` 檔案：
    
        paraview aa.foam

2.  如要繪製動壓場，可選擇 `p_rgh` 並使用 `Surface` 繪製。

3.  欲分離出物體，需透過 `Threshold` 工具：
    1.  從 `Pipeline Browser` 處，在 `aa.foam` 點選 `Threshold`. 出現 `Threshold 1` 。在 `Threshold 1` 中的 `Properties` 之 `Scalars` 選擇 `ZoneID`, 並設定其值之 `Minimum = 0`, `Maximum = 0` 。顯示此 `Threshold 1` 並關閉 `aa.foam`, 可顯示出背景流體。
    
    2.  在 `Threshold 1` 中再做一次 `Threshold` 工具，出現 `Threshold 2` 。在 `Threshold 2` 處之 `Properties` 之 `Scalars` 選擇 `cellTypes`, 設定值 `Minimum = 0`, `Maximum = 1` 。開啟 `Threshold 2` 並關閉 `Threshold 1`, 可出現扣除浮體網格之背景流場。
    
    3.  在 `aa.foam` 點選 `Threshold`, 出現 `Threshold 3` 。在 `Threshold 3` 中的 `Properties` 之 `Scalars` 選擇 `ZoneID`, 並設定其值之 `Minimum = 1`, `Maximum = 1` 。點開 `Advanced Properties`, 在 `Transforming` 中設定 `Translation = (0, -0.2, 0)` 。顯示此 `Threshold 3` 可出現浮體附近的流場。
    
    4.  僅開啟 `Threshold2` 與 `Threshold3`, 並在 `Orientation Axes` 中點選 `Camera Paralle Projection`, 可出現浮體被挖空之波浪流場。


### 繪製繫纜線

1.  在 ParaView 中開啟纜線的 VTK 檔。以 Overset 案例為例，VTK 檔位於
    
        background/Mooring/VTK/mdv2_pt.pvd

2.  在 `Pipeline Browser` 中點選 `mdv2_pt.vtk.pvd`, 使用 `Transforming` 將纜線平移到與浮體一樣的位置。


## 波高、位移量與纜繩張力繪圖

繪圖可於資料夾 `Plots` 中進行。見 <./tutorials/overset_parallel/background/Plots/postProcessing.ipynb> 的說明與程式碼。

