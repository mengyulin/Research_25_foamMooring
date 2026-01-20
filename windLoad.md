
# Table of Contents

1.  [風力模型](#org07f6616)
    1.  [週期性均勻風壓](#orge878f65)
    2.  [Theodorsen 薄機翼理論](#orgfe22ca0)
2.  [風力函式庫之應用](#orgf8d2e7a)
    1.  [週期性均勻風壓](#org67a7641)
        1.  [Step 1 放到 FOAM<sub>USER</sub><sub>LIBBIN</sub>](#org4f94e8a)
        2.  [Step 2 在 `/background/system/controlDict` 載入 library](#orgd6e731b)
        3.  [Step 3 在 `/background/constant/dynamicMeshDict` 使用 restraint](#orgeb92801)



<a id="org07f6616"></a>

# 風力模型


<a id="orge878f65"></a>

## 週期性均勻風壓

設定風壓 $p(t)$ 為週期性變化且均勻分佈於浮體上表面：

\begin{equation}
\label{eq:uniPressure}
p(t) = p_0 + A\sin(\omega t + \phi)
\end{equation}

其中 $p_0$ 為平均壓力值、$A$ 為振盪壓力之振幅、$\omega$ 為角頻率 (可設與波浪相同)、$\phi$ 則為相位角。


<a id="orgfe22ca0"></a>

## Theodorsen 薄機翼理論

進行中。


<a id="orgf8d2e7a"></a>

# 風力函式庫之應用


<a id="org67a7641"></a>

## 週期性均勻風壓


<a id="org4f94e8a"></a>

### Step 1 放到 FOAM<sub>USER</sub><sub>LIBBIN</sub>

下載檔案 [libuniformWindPressureRestraint.so](./libs/libuniformWindPressureRestraint.so), 於同資料夾中執行：

    cp libuniformWindPressureRestraint.so $FOAM_USER_LIBBIN


<a id="orgd6e731b"></a>

### Step 2 在 `/background/system/controlDict` 載入 library

將：

    libs            (overset fvMotionSolvers sixDoFMooring);

修改為：

    libs ("liboverset.so" "libfvMotionSolvers.so" "libsixDoFMooring.so" "libuniformWindPressureRestraint.so.so");


<a id="orgeb92801"></a>

### Step 3 在 `/background/constant/dynamicMeshDict` 使用 restraint

在 `restraints` 加入參數設定值，例如以下接續在 `moorDynR2_pt` 之後的設定：

    restraints
    {
      moorDynR2_pt
      {
        sixDoFRigidBodyMotionRestraint  moorDynR2;
        couplingMode       "POINT";
        inputFile          "Mooring/lines_v2_point.txt";
        refAttachmentPt
        (
          (-0.1      0.1    -0.0736)
          (-0.1     -0.1    -0.0736)
          ( 0.1      0.1    -0.0736)
          ( 0.1     -0.1    -0.0736)
        );
        writeMooringVTK    true;
        vtkPrefix         "mdv2_pt";
        vtkStartTime       0;
        outerCorrector     1;
      }
    
      windForce
        {
          sixDoFRigidBodyMotionRestraint  uniformWindPressureRestraint;
          // type    uniformWindPressureRestraint;
    
          // Cuboid dimensions
          Lx              0.2;
          Ly              0.2;
          Lz              0.132;
    
          // 施力點（剛體座標系，單位 m）
          // 例如：浮體幾何中心上方 5 cm
          rLocal  (0 0 0.05);
    
          // 施力方向（剛體座標系單位向量）
          // 例如：沿 +Z 方向的「壓力 * 面積」等效力
          nLocal  (0 0 1);
    
          // 壓力模型參數（自行調整）
          p0      0;          // 平均值（Pa）
          A       50;         // 振幅（Pa）
          omega   3.490659;   // 角頻率 rad/s, omega = 2 pi/T, T: wave period
          phi     0;          // 初相位（rad）
          beta    1;          // 指數；=1 為純正弦，可用 >1 做非線性整形
        }

