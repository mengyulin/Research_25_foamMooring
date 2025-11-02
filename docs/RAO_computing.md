

# 6-DoF Orientation 的輸出格式與 Pitch 角計算

OpenFOAM 的六自由度求解器 (如 `overInterDyMFoam`, `sixDoFRigidBodyMotionSolver`) 會在 log 檔中輸出剛體的位置矩陣：

    6-DoF rigid body motion
        Orientation: (xx xy xz  yx yy yz  zx zy zz)

這 9 個數值組成 3×3 旋轉矩陣：

$$
R = \begin{bmatrix}
R_{11} & R_{12} & R_{13} \\
R_{21} & R_{22} & R_{23} \\
R_{31} & R_{32} & R_{33}
\end{bmatrix}
$$

在輸出中順序為 row-major：
$$(xx, xy, xz,  yx, yy, yz,  zx, zy, zz)$$

例如：

    Orientation: (1 0 -5.2e-13  0 1 0  5.2e-13 0 1)

對應矩陣：

$$
R = \begin{bmatrix}
1 & 0 & -5.2\times10^{-13} \\
0 & 1 & 0 \\
5.2\times10^{-13} & 0 & 1
\end{bmatrix}
$$

Pitch angle (俯仰角) 可依 ZYX (yaw-pitch-roll) 旋轉順序求得：

$$
\theta_{\mathrm{pitch}} = \mathrm{atan2}(-R_{31}, \sqrt{R_{11}^2 + R_{21}^2})
$$

這個式子比傳統的 `arccos` 方法更穩定，能保留正負號並避免角度跳變。

程式碼為：

    # 假設 y1..y9 為 Orientation 的九個欄位
    R11, R21, R31 = y1, y4, y7
    pitch_rad = np.arctan2(-R31, np.sqrt(R11**2 + R21**2))
    pitch_deg = np.degrees(pitch_rad)


# 利用 FFT 與最小平方法擬合求取主頻與振幅

****目的:**** 在規律波（Stokes II）作用下，計算浮體各自由度（Surge、Heave、Pitch）的週期性響應，並進而求出 RAO。

****步驟概要:****

1.  從模擬輸出讀取時間序列。
2.  使用 FFT 檢查頻譜，確認主頻是否接近理論頻率 $f = 1/T$ 。
3.  使用理論頻率進行單頻最小平方擬合，以求得穩態振幅與相位。

****FFT 計算範例：****

    freq, amp, f_peak, A_peak = compute_fft(time, heave)
    plt.plot(freq, amp)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude (m)")
    plt.title("Heave Spectrum")

****最小平方擬合方法：****

$$
y(t) \approx c + a\cos(2\pi f t) + b\sin(2\pi f t)
$$

求得：

$$
R = \sqrt{a^2 + b^2}, \quad \phi = \tan^{-1}\!\left(\frac{b}{a}\right)
$$

Python 範例：

    yhat, idx_ss, R, phi = fit_main_sinusoid(time, heave, f_theory, use_steady=True)


# RAO（Response Amplitude Operator）的計算

定義：

$$
\mathrm{RAO}(\omega) = \frac{X(\omega)}{a}
$$

其中：

-   $X(\omega)$: 浮體運動的複數振幅 (由擬合得 $R$ 與 $\phi$)
-   $a = H/2$: 入射波第一階振幅
-   單位：
    -   Surge, Heave：m/m
    -   Pitch：rad/m

****計算範例：****

    H = 0.12
    T = 1.8
    a = H / 2
    f_theory = 1.0 / T
    
    # R, phi 由擬合結果而得
    rao_heave_mag = R_heave / a
    rao_heave_phase = np.degrees(phi_heave)
    print(f"|RAO_heave| = {rao_heave_mag:.3f} m/m,  Phase = {rao_heave_phase:.2f} deg")


# FFT 與擬合方法之比較

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">方法</th>
<th scope="col" class="org-left">優點</th>
<th scope="col" class="org-left">缺點</th>
<th scope="col" class="org-left">適用情況</th>
</tr>
</thead>

<tbody>
<tr>
<td class="org-left">FFT 主峰法</td>
<td class="org-left">快速、可檢查諧波</td>
<td class="org-left">受窗長影響</td>
<td class="org-left">初步確認主頻、檢查噪音</td>
</tr>


<tr>
<td class="org-left">最小平方法擬合</td>
<td class="org-left">精確估振幅與相位</td>
<td class="org-left">需假定頻率已知</td>
<td class="org-left">單頻波、穩態分析、RAO 計算</td>
</tr>
</tbody>
</table>


# RAO 檢核與結果輸出

-   比較擬合主頻與理論頻率：
    
    $$
      \Delta f = f_{\rm meas} - \frac{1}{T}
      $$
    
    若 $|\Delta f| < 1/T_{win}$，則屬於解析度內的誤差。

-   匯出結果範例：
    
        [RAO] Single-case results (normalized by a = H/2):
          Surge : |RAO| = 0.82 m/m,  ∠RAO = -4.1 deg
          Heave : |RAO| = 0.94 m/m,  ∠RAO = 2.7 deg
          Pitch : |RAO| = 0.015 rad/m, ∠RAO = -1.2 deg

結果可輸出至 CSV 以供繪製 RAO - $\omega$ 曲線。


# 附錄：Pitch angle 的計算法補充說明


## 方向餘弦矩陣（Direction Cosine Matrix, DCM）

OpenFOAM 在 6-DoF 模擬中使用三維旋轉矩陣 $R$ 來描述剛體姿態，
其輸出格式為：

$$
R = \begin{bmatrix}
R_{11} & R_{12} & R_{13} \\
R_{21} & R_{22} & R_{23} \\
R_{31} & R_{32} & R_{33}
\end{bmatrix}
$$

輸出順序為 row-major，即 `(xx xy xz  yx yy yz  zx zy zz)` 。

在物理意義上，矩陣的每一欄代表「物體座標軸在全域座標下的方向餘弦」，
因此 $R_{31}$ 表示「全域 z 軸在物體 x 軸上的投影分量」。


## ZYX 旋轉順序 (Yaw&#x2013;Pitch&#x2013;Roll)

若採航空常用的 ZYX 旋轉順序，
則從歐拉角 $(\psi,\theta,\phi)$（依序為 yaw, pitch, roll）生成旋轉矩陣：

$$
R =
R_z(\psi)\, R_y(\theta)\, R_x(\phi)
$$

展開後：

$$
R = \begin{bmatrix}
c_\psi c_\theta & c_\psi s_\theta s_\phi - s_\psi c_\phi & c_\psi s_\theta c_\phi + s_\psi s_\phi \\
s_\psi c_\theta & s_\psi s_\theta s_\phi + c_\psi c_\phi & s_\psi s_\theta c_\phi - c_\psi s_\phi \\
-s_\theta       & c_\theta s_\phi                         & c_\theta c_\phi
\end{bmatrix}
$$

因此：

$$
R_{31} = -\sin\theta, \quad
R_{11} = \cos\psi \cos\theta, \quad
R_{21} = \sin\psi \cos\theta
$$


## 由旋轉矩陣反推 pitch angle

由上式可得：

$$
\theta = \operatorname{atan2}(-R_{31}, \sqrt{R_{11}^2 + R_{21}^2})
$$

此式的特點是：

-   使用 `atan2` 可保留正負號 (上仰為正，下俯為負)。
-   可避免因 `acos` 限制在 $[0, \pi]$ 區間而造成跳變。
-   在數值模擬中，即使 pitch 振幅僅數度，仍能保持連續性。


## 小角度驗證

若 pitch 很小：

$$
R_{31} \approx -\sin\theta \approx -\theta
$$

因此可近似：

$$
\theta \approx -R_{31}
$$

這在波浪激勵的小幅振動情況下常用作簡化驗證。


## Python 實作範例

假設由 OpenFOAM 擷取的 Orientation 九個欄位為：

    (y1 y2 y3  y4 y5 y6  y7 y8 y9)
    = (R11 R12 R13  R21 R22 R23  R31 R32 R33)

則可用下列程式計算 pitch angle：

    import numpy as np
    
    # 從 OpenFOAM log 檔讀入 Orientation 九個欄位
    R11, R21, R31 = y1, y4, y7
    
    # 由 ZYX 旋轉順序反算 pitch
    pitch_rad = np.arctan2(-R31, np.sqrt(R11**2 + R21**2))
    pitch_deg = np.degrees(pitch_rad)


## 實際案例說明

例：OpenFOAM log 中輸出

    Orientation: (1 0 -5.2e-13  0 1 0  5.2e-13 0 1)

對應矩陣：

$$
R_{31} = 5.2\times10^{-13}, \quad R_{11}=1, \quad R_{21}=0
$$

則：

$$
\theta = \operatorname{atan2}(-5.2\times10^{-13}, 1) \approx -5.2\times10^{-13}\ \text{rad} \approx 0.0°,
$$

表示浮體幾乎水平。

