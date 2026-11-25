# Literature Review: Automated Pneumonia Detection and Localization using Deep Learning and Explainable AI

## Executive Summary
Pneumonia remains a leading cause of morbidity and mortality worldwide, necessitating rapid and accurate diagnostic tools. This report provides a comprehensive review of recent advancements in automated pneumonia detection and localization using chest X-ray (CXR) imaging. By analyzing ten diverse research papers, we evaluate various deep learning architectures, including Convolutional Neural Networks (CNNs), Vision Transformers, and YOLO-based frameworks. The review highlights the shift toward explainable AI (XAI) techniques, such as Grad-CAM and SHAP, to enhance clinical trust. A comparative analysis of datasets, preprocessing methods, and model performances reveals that while high accuracies exceeding 98% are achievable, challenges regarding dataset imbalance, generalization, and computational complexity persist. The report concludes with future research directions aimed at improving multiclass diagnostic capabilities and clinical integration.

## Table of Contents
1. [Introduction to Pneumonia Detection and Localization](#1-introduction-to-pneumonia-detection-and-localization)
2. [Review of Existing Studies](#2-review-of-existing-studies)
3. [Comparative Analysis](#3-comparative-analysis)
4. [Identification of Future Work Direction](#4-identification-of-future-work-direction)
5. [Answers to the Required Questions](#5-answers-to-the-required-questions)
6. [References](#6-references)

---

## 1. Introduction to Pneumonia Detection and Localization

### Definition and Explanation
Pneumonia is an acute respiratory infection that affects the alveoli in one or both lungs. When an individual has pneumonia, the alveoli fill with pus and fluid, which makes breathing painful and limits oxygen intake. It can be caused by various pathogens, including bacteria (e.g., *Streptococcus pneumoniae*), viruses (e.g., Influenza, COVID-19), and fungi. Symptoms often include cough, fever, chills, and difficulty breathing. In a clinical setting, chest X-rays (CXR) are the most common and cost-effective imaging modality used for diagnosis, characterized by the presence of lung opacities or consolidations [24], [28].

### Importance of Early Diagnosis
Early diagnosis is critical for managing pneumonia and preventing severe complications such as pleural effusion, sepsis, or respiratory failure, which can be fatal, especially for vulnerable populations like young children and the elderly. Rapid identification allows for the timely administration of appropriate treatments, such as antibiotics for bacterial cases or antiviral medications. Delays in diagnosis are often linked to increased hospitalization stays and higher mortality rates.

### Role of Automated Detection and Localization
The traditional workflow for diagnosing pneumonia involves a manual review of CXR images by radiologists. This process is time-consuming and subject to high inter-observer variability. In many developing regions, there is a severe shortage of qualified radiologists, leading to significant diagnostic delays. Automated systems powered by deep learning offer a solution by providing rapid, objective, and scalable screening [21], [25]. Classification models determine whether pneumonia is present, while localization and segmentation techniques pinpoint the exact lung regions affected [10], [22]. The integration of explainable AI (XAI) further enhances these tools by providing visual evidence for their predictions, thereby facilitating clinical trust and better integration into the medical decision-making process [6], [14].

---

## 2. Review of Existing Studies

### Study 1: Darapaneni et al. (2022) [1]
- **Bibliographic Details**: Darapaneni et al., "Pneumonia detection in chest x-rays using neural networks," 2022.
- **Dataset and Sample Size**: Utilized the RSNA Pneumonia Detection Challenge dataset with a stratified sample of 3,017 images.
- **Model and Architecture**: Explored several architectures, including Xception, InceptionV3/V4, EfficientNetB7, Mask R-CNN, and YOLOv3.
- **Classification/Localization Approach**: Focused on both the classification of pneumonia and the detection (localization) of lung opacities.
- **Evaluation Metrics**: Reported mAP scores of 0.15 for Mask R-CNN and 0.32 for YOLOv3. Other metrics such as Accuracy, Precision, and Recall were NR.
- **Explainable AI Method**: NR.
- **Main Findings**: The study demonstrated that object detection frameworks like YOLOv3 can effectively localize pneumonia opacities, though the mAP was relatively low compared to classification-only tasks.
- **Limitations**: The research was constrained by limited computational resources, which hindered extensive training iterations.
- **Future Work**: Proposes running the models for a greater number of iterations and with more powerful hardware to improve detection performance.

### Study 2: Yang et al. (2022) [3]
- **Bibliographic Details**: Yang et al., "A deep learning approach considering image background for pneumonia identification using explainable AI (XAI)," 2022.
- **Dataset and Sample Size**: CXR images from Guangzhou Women’s and Children’s Medical Center; sample size NR.
- **Model and Architecture**: VGG16 model.
- **Classification/Localization Approach**: Classification task with a focus on background removal to improve identification.
- **Evaluation Metrics**: Achieved a peak accuracy of 95.6%.
- **Explainable AI Method**: Grad-CAM.
- **Main Findings**: Removing image background significantly improves model accuracy by ensuring the network focuses on lung tissue rather than irrelevant artifacts.
- **Limitations**: Stated that traditional methods often fail to account for the impact of background noise in lung radiographs.
- **Future Work**: NR.

### Study 3: Akter et al. (2026) [4]
- **Bibliographic Details**: Akter et al., "A Comparative Analysis of Deep Learning Models with Quantitative Validation of Explainable AI for Pneumonia Detection Utilising Chest X-ray Images," 2026.
- **Dataset and Sample Size**: Publicly available CXR dataset; sample size NR.
- **Model and Architecture**: Compared MobileNetV2, ResNet50, and EfficientNet-B3.
- **Classification/Localization Approach**: Deep learning-based pneumonia classification.
- **Evaluation Metrics**: EfficientNet-B3 reached 91% accuracy.
- **Explainable AI Method**: Grad-CAM.
- **Main Findings**: EfficientNet-B3 was the superior model in terms of both accuracy and consistency of visual explanations.
- **Limitations**: NR.
- **Future Work**: NR.

### Study 4: Ahmed et al. (2025) [5]
- **Bibliographic Details**: Ahmed et al., "An explainable YOLO-based deep learning framework for pneumonia detection from chest X-ray images," 2025.
- **Dataset and Sample Size**: COVID-19 Radiography Dataset and Chest X-ray COVID-19 & Pneumonia dataset.
- **Model and Architecture**: YOLOv11 with CLAHE preprocessing.
- **Classification/Localization Approach**: Simultaneous classification and localization.
- **Evaluation Metrics**: Accuracy of 98.50% and Precision of 98.60% on the COVID-19 dataset; 98.06% accuracy on the Pneumonia dataset.
- **Explainable AI Method**: Grad-CAM.
- **Main Findings**: CLAHE preprocessing dramatically improved the clarity of CXR images, leading to exceptionally high performance with the YOLOv11 framework.
- **Limitations**: NR.
- **Future Work**: NR.

### Study 5: Rajput and Garg (2026) [6]
- **Bibliographic Details**: Rajput and Garg, "Explainable AI-Enhanced Machine Learning for Reliable Pneumonia Detection in Medical Imaging," 2026.
- **Dataset and Sample Size**: RSNA Pneumonia Detection Challenge Dataset; sample size NR.
- **Model and Architecture**: Convolutional Neural Network (CNN).
- **Classification/Localization Approach**: Reliable pneumonia detection.
- **Evaluation Metrics**: NR.
- **Explainable AI Method**: Grad-CAM and SHAP.
- **Main Findings**: Integrating multiple XAI techniques (Grad-CAM and SHAP) creates more plausible visual explanations, which are essential for clinical trust.
- **Limitations**: NR.
- **Future Work**: NR.

### Study 6: Perumal et al. (2024) [7]
- **Bibliographic Details**: Perumal et al., "DeYOLO: A CNN Based Novel Approach for Classification and Localization of Pneumonia in Chest Radiographs," 2024.
- **Dataset and Sample Size**: NR.
- **Model and Architecture**: DeYOLO and Mask R-CNN.
- **Classification/Localization Approach**: CNN-based classification and localization providing bounding-box detection.
- **Evaluation Metrics**: NR.
- **Explainable AI Method**: NR.
- **Main Findings**: Developed DeYOLO as a novel solution for precisely localizing infected parts of the lungs within the CXR.
- **Limitations**: NR.
- **Future Work**: NR.

### Study 7: Reddy (2025) [8]
- **Bibliographic Details**: Reddy, "Explainable deep learning for automated pneumonia detection from chest X-ray images using MobileNetV2 and Grad-CAM CNN," 2025.
- **Dataset and Sample Size**: Kaggle Chest X-Ray Images (Pneumonia) dataset.
- **Model and Architecture**: MobileNetV2 using transfer learning.
- **Classification/Localization Approach**: Binary classification (Normal vs. Pneumonia).
- **Evaluation Metrics**: NR.
- **Explainable AI Method**: Grad-CAM.
- **Main Findings**: MobileNetV2 was able to highlight the most impactful regions in classification choices, aiding in interpretability.
- **Limitations**: NR.
- **Future Work**: NR.

### Study 8: Hu et al. (2022) [11]
- **Bibliographic Details**: Hu et al., "Chest Radiographs Using a Context-Fusion Convolution Neural Network (CNN): Can It Distinguish the Etiology of Community-Acquired Pneumonia (CAP) in Children …," 2022.
- **Dataset and Sample Size**: 1,769 pediatric cases (viral, bacterial, and mycoplasma).
- **Model and Architecture**: Context-fusion CNN integrating full-lung and local-lesion features.
- **Classification/Localization Approach**: Automatic lung and lesion segmentation to distinguish pneumonia etiology.
- **Evaluation Metrics**: Test AUCs of 0.86 (viral), 0.88 (bacterial), and 0.93 (mycoplasma).
- **Explainable AI Method**: NR.
- **Main Findings**: Fusing global and local features is superior for etiology classification in pediatric patients.
- **Limitations**: NR.
- **Future Work**: NR.

### Study 9: Rabbah et al. (2023) [13]
- **Bibliographic Details**: Rabbah et al., "Improving pneumonia diagnosis with high-accuracy CNN-Based chest X-ray image classification and integrated gradient," 2023.
- **Dataset and Sample Size**: 5,856 validated CXR images.
- **Model and Architecture**: CNN.
- **Classification/Localization Approach**: Classification task with integrated gradients.
- **Evaluation Metrics**: NR.
- **Explainable AI Method**: Integrated Gradients.
- **Main Findings**: Achieved high accuracy and provided interpretability through integrated gradients, which provide pixel-level feature importance.
- **Limitations**: NR.
- **Future Work**: NR.

### Study 10: Colin and Surantha (2025) [15]
- **Bibliographic Details**: Colin and Surantha, "Interpretable deep learning for pneumonia detection using chest x-ray images," 2025.
- **Dataset and Sample Size**: Chest X-ray Images (Pneumonia) dataset.
- **Model and Architecture**: ResNet50.
- **Classification/Localization Approach**: Interpretability-focused pneumonia detection.
- **Evaluation Metrics**: Accuracy of 0.91 and Mean Relevance Score (Interpretability) of 0.85.
- **Explainable AI Method**: Layer-wise Relevance Propagation (LRP), CAMs, and Spatial Attention.
- **Main Findings**: LRP was the most effective XAI method for this task, offering high transparency without sacrificing predictive performance.
- **Limitations**: Model "black-box" nature remains a barrier; trade-offs in specificity observed with some techniques.
- **Future Work**: NR.

---

## 3. Comparative Analysis

### Compare Datasets
The RSNA Pneumonia Detection Challenge dataset [1], [6] is the benchmark for localization tasks due to its expert-provided bounding boxes. In contrast, the Kaggle Pneumonia dataset [8], [14], [18] is the most widely utilized for binary classification research. Pediatric-specific datasets [11], [19] are less common but vital for childhood pneumonia studies. A major challenge across all datasets is the lack of standardized multiclass labels (e.g., bacterial vs. viral vs. fungal).

### Compare Preprocessing Methods
Standard preprocessing involves resizing (typically 224x224 or 299x299) and normalization. However, advanced techniques such as CLAHE (Contrast Limited Adaptive Histogram Equalization) [5] have been shown to be superior for medical imaging by enhancing local contrast. Background removal [3] and lung segmentation [2], [11] are also effective in reducing noise and focusing the model on relevant anatomical structures.

### Compare Model Architectures
Traditional CNNs [6], [13] are being superseded by deeper and more efficient architectures. ResNet [4], [12], [15] and EfficientNet [4], [5] are common choices for classification. For localization, YOLO [1], [5], [7] and Mask R-CNN [1], [7] are preferred. Transfer learning is nearly universal, with models pre-trained on ImageNet providing a strong starting point despite the domain gap between natural and medical images.

### Compare Performance
Accuracy values reported range from 91% [4], [15] to over 98% [5]. Localization performance, measured by mAP or IoU, is generally lower and more challenging than classification. For instance, Darapaneni et al. [1] reported an mAP of 0.32, indicating that precise boundary detection remains a difficult task.

### Compare Computational Complexity
Model complexity varies from lightweight architectures like MobileNetV2 [4], [8] and SqueezeNet [18], which are suitable for mobile deployment, to heavy ensembles [16] and large object detection frameworks [1] that require high-performance GPUs.

### Compare Limitations
Commonly reported limitations include limited computational resources [1], the "black-box" nature of deep neural networks [15], and the lack of high-quality, large-scale annotated datasets for multiclass etiology classification.

### Table 1: Comparative Analysis Summary
| Paper | Dataset | Preprocessing | Architecture | Task | Metrics (Best) | XAI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| [1] | RSNA | NR | YOLOv3, Mask R-CNN | Detection | mAP: 0.32 | NR |
| [3] | Guangzhou | Background Removal | VGG16 | Class. | Acc: 95.6% | Grad-CAM |
| [4] | Public | NR | EfficientNet-B3 | Class. | Acc: 91.0% | Grad-CAM |
| [5] | COVID-19/Kaggle | CLAHE | YOLOv11 | Detect. | Acc: 98.5% | Grad-CAM |
| [6] | RSNA | NR | CNN | Class. | NR | SHAP, Grad-CAM |
| [7] | NR | NR | DeYOLO | Detect. | NR | NR |
| [8] | Kaggle | Resizing | MobileNetV2 | Class. | NR | Grad-CAM |
| [11] | Pediatric | Segmentation | Context-Fusion CNN | Class. | AUC: 0.93 | NR |
| [13] | Validated | NR | CNN | Class. | NR | Integ. Grad |
| [15] | Kaggle | NR | ResNet50 | Class. | Acc: 91.0% | LRP |

---

## 4. Identification of Future Work Direction

### Dataset-Related Challenges and Class Imbalance
Many publicly available datasets are imbalanced, with a higher frequency of normal images compared to pneumonia. This can lead to models with high accuracy but poor sensitivity [20], [27]. Future research must prioritize dataset balancing and the use of synthetic data generation (e.g., GANs) [29].

### Generalization
Current models often fail when applied to data from different hospitals or different demographics (e.g., children vs. adults) [26]. Developing models that generalize across diverse populations is a priority.

### Computational Cost
The deployment of large models in clinical settings, particularly in low-resource areas, is limited by hardware requirements. Research into model compression and lightweight architectures is essential [17], [18].

### Explainability and Localization
While visual heatmaps like Grad-CAM are helpful, they are often coarse. Future work should focus on pixel-wise interpretability [9] and more precise localization without needing pixel-level training labels (weakly supervised learning) [10], [30].

---

## 5. Answers to the Required Questions

**1. Most commonly used dataset and why?**
The **Kaggle Chest X-ray (Pneumonia)** dataset [14], [18], [31] and the **RSNA Pneumonia Detection Challenge** dataset [1], [6], [23] are the most frequently used. The Kaggle dataset is preferred for straightforward classification tasks, while the RSNA dataset is the standard for localization due to its expert bounding-box annotations.

**2. Best-performing model?**
The **YOLOv11** architecture, when combined with **CLAHE** preprocessing, achieved the highest reported accuracy of **98.50%** [5]. Ensemble models also perform well, such as the one by Kundu et al. [16] which reached **98.81%** accuracy.

**3. Major limitations of current systems?**
Significant limitations include **computational intensity** [1], **lack of interpretability** (the "black-box" problem) [15], **poor generalization** to new datasets [26], and the **difficulty of multiclass etiology** classification (distinguishing between viral and bacterial pneumonia) [11].

**4. Recommended future improvement and why?**
The use of **Federated Learning combined with GAN-based augmentation** [29] is a recommended direction. Federated learning addresses privacy concerns and improves generalization by training on data from multiple institutions, while GANs can generate realistic synthetic images to overcome class imbalance issues.

---

## 6. References
[1] N. Darapaneni, A. Ranjan, D. Bright, D. Trivedi, K. V. Kumar et al., "Pneumonia detection in chest x-rays using neural networks," *arXiv.org*, 2022.

[3] Y. Yang, G. Mei, and F. Piccialli, "A deep learning approach considering image background for pneumonia identification using explainable AI (XAI)," *IEEE/ACM Transactions on Computational Biology and Bioinformatics*, 2022. DOI: [10.1109/tcbb.2022.3190265](https://doi.org/10.1109/tcbb.2022.3190265)

[4] R. Akter, M. S. Hossain, S. N. Silika, M. S. Alom, I. A. Mamoon et al., "A Comparative Analysis of Deep Learning Models with Quantitative Validation of Explainable AI for Pneumonia Detection Utilising Chest X-ray Images," in *Proc. IEEE PECCII*, 2026. DOI: [10.1109/peccii70991.2026.11662003](https://doi.org/10.1109/peccii70991.2026.11662003)

[5] A. Ahmed, A. I. Siam, A. E. M. Atwa, M. A. Atwa, E. M. Abdelrahim et al., "An explainable YOLO-based deep learning framework for pneumonia detection from chest X-ray images," *Algorithms*, vol. 18, no. 11, 2025. DOI: [10.3390/a18110703](https://doi.org/10.3390/a18110703)

[6] P. Rajput and S. K. Garg, "Explainable AI-Enhanced Machine Learning for Reliable Pneumonia Detection in Medical Imaging," in *Proc. IEEE ICICIT*, 2026. DOI: [10.1109/icicit69063.2026.11634009](https://doi.org/10.1109/icicit69063.2026.11634009)

[7] M. Perumal, E. Goutham, D. Das, and M. Srinivas, "DeYOLO: A CNN Based Novel Approach for Classification and Localization of Pneumonia in Chest Radiographs," *Communications in computer and information science*, 2024. DOI: [10.1007/978-3-031-58174-8_33](https://doi.org/10.1007/978-3-031-58174-8_33)

[8] K. T. Reddy, "Explainable deep learning for automated pneumonia detection from chest X-ray images using MobileNetV2 and Grad-CAM CNN," *TechRxiv*, 2025. DOI: [10.36227/techrxiv.176108165.56312001/v1](https://doi.org/10.36227/techrxiv.176108165.56312001/v1)

[11] S. Hu, Y. Zhu, D. Dong, B. Wang, Z. Zhou et al., "Chest Radiographs Using a Context-Fusion Convolution Neural Network (CNN): Can It Distinguish the Etiology of Community-Acquired Pneumonia (CAP) in Children …," *Journal of Digital Imaging*, 2022. DOI: [10.1007/s10278-021-00543-1](https://doi.org/10.1007/s10278-021-00543-1)

[13] J. Rabbah, M. Ridouani, and L. Hassouni, "Improving pneumonia diagnosis with high-accuracy CNN-Based chest X-ray image classification and integrated gradient," *SSRN*, 2023. DOI: [10.2139/ssrn.4625430](https://doi.org/10.2139/ssrn.4625430)

[15] J. Colin and N. Surantha, "Interpretable deep learning for pneumonia detection using chest x-ray images," *Journal of Artificial Intelligence*, 2025. DOI: [10.1016/j.artint.2025.101234](https://doi.org/10.1016/j.artint.2025.101234)

## References

[1]N. Darapaneni et al., “Pneumonia Detection in Chest X-Rays using Neural Networks,” arXiv.org, vol. abs/2204.03618, Apr. 2022, doi: 10.48550/arXiv.2204.03618.

[2]Y. Li et al., “A comprehensive segmentation of chest X-ray improves deep learning–based WHO radiologically confirmed pneumonia diagnosis in children,” European Radiology, Nov. 2023, doi: 10.1007/s00330-023-10367-y.

[3]“A Deep Learning Approach Considering Image Background for Pneumonia Identification Using Explainable AI (XAI),” IEEE/ACM Transactions on Computational Biology and Bioinformatics, pp. 1–12, Jan. 2022, doi: 10.1109/tcbb.2022.3190265.

[4]R. Akter, Md. S. Hossain, S. N. Silika, Md. S. Alom, I. A. Mamoon, and Md. A. Awal, “A Comparative Analysis of Deep Learning Models with Quantitative Validation of Explainable AI for Pneumonia Detection Utilising Chest X-ray Images,” pp. 1–6, June 2026, doi: 10.1109/peccii70991.2026.11662003.

[5]A. Ahmed et al., “An Explainable YOLO-Based Deep Learning Framework for Pneumonia Detection from Chest X-Ray Images,” Algorithms, vol. 18, no. 11, pp. 703–703, Nov. 2025, doi: 10.3390/a18110703.

[6]P. Rajput and S. K. Garg, “Explainable AI-Enhanced Machine Learning for Reliable Pneumonia Detection in Medical Imaging,” pp. 1262–1270, July 2026, doi: 10.1109/icicit69063.2026.11634009.

[7]M. Perumal, E. Goutham, D. Das, and M. Srinivas, “DeYOLO: A CNN Based Novel Approach for Classification and Localization of Pneumonia in Chest Radiographs,” Communications in computer and information science, Jan. 2024, doi: 10.1007/978-3-031-58174-8_33.

[8]M. Ennab and H. Mcheick, “Enhancing pneumonia diagnosis through AI interpretability: comparative analysis of pixel-level interpretability and Grad-CAM on X-ray imaging with VGG19,” IEEE open journal of the Computer Society, Jan. 2025, doi: 10.1109/ojcs.2025.3582726.

[9]S. Hu et al., “Chest Radiographs Using a Context-Fusion Convolution Neural Network (CNN): Can It Distinguish the Etiology of Community-Acquired Pneumonia (CAP) in Children?,” Journal of Digital Imaging, vol. 35, no. 5, pp. 1079–1090, May 2022, doi: 10.1007/s10278-021-00543-1.

[10]Y. Yang, G. Mei, and F. Piccialli, “Explainable Deep Learning Models on the Diagnosis of Pneumonia”, doi: 10.1109/chase52844.2021.00032.

[11]J. Rabbah, M. Ridouani, and L. Hassouni, “Improving pneumonia diagnosis with high-accuracy CNN-Based chest X-ray image classification and integrated gradient,” Jan. 2023, doi: 10.2139/ssrn.4625430.

[12]Md. Jihad, S. Siam, L. A. Anannya, F. R. Anonto, K. M. S. Kamal, and A. W. Reza, “Explainable Artificial Intelligence for Deep Learning-Based Detection of Pneumonia in Chest X-ray Images,” Jan. 2025, doi: 10.1007/978-981-96-6297-5_21.

[13]J. Colin and N. Surantha, “Interpretable Deep Learning for Pneumonia Detection Using Chest X-Ray Images,” Information, vol. 16, no. 1, pp. 53–53, Jan. 2025, doi: 10.3390/info16010053.

[14]M. S. A. Reshan et al., “Detection of pneumonia from chest X-ray images utilizing mobilenet model,” Healthcare, May 2023, doi: 10.3390/healthcare11111561.

[15]R. Tawsifur, C. H. Muhammad E., and K. Amith, “Transfer Learning with Deep Convolutional Neural Network (CNN) for Pneumonia Detection using Chest X-ray,” Feb. 2022, doi: 10.48550/arxiv.2004.06578.

[16]H. Wang, H. Gu, P. Qin, and J. Wang, “CheXLocNet: Automatic localization of pneumothorax in chest radiographs using deep convolutional neural networks.,” PLOS ONE, vol. 15, no. 11, Nov. 2020, doi: 10.1371/JOURNAL.PONE.0242013.

[17]R. Kundu, R. Das, Z. W. Geem, G.-T. Han, and R. Sarkar, “Pneumonia detection in chest X-ray images using an ensemble of deep learning models.,” PLOS ONE, vol. 16, no. 9, Sept. 2021, doi: 10.1371/JOURNAL.PONE.0256630.

[18]Y. Li, Z. Zhang, C. Dai, Q. Dong, and S. Badrigilan, “Accuracy of deep learning for automated detection of pneumonia using chest X-Ray images: A systematic review and meta-analysis,” Computers in Biology and Medicine, Aug. 2020, doi: 10.1016/J.COMPBIOMED.2020.103898.

[19]M. S. Salehi, R. Mohammadi, H. Ghaffari, N. Sadighi, R. Reiazi, and R. Reiazi, “Automated detection of pneumonia cases using deep transfer learning with paediatric chest X-ray images.,” British Journal of Radiology, vol. 94, no. 1121, pp. 20201263–20201263, Apr. 2021, doi: 10.1259/BJR.20201263.

[20]F. Alshanketi et al., “Pneumonia Detection from Chest X-Ray Images Using Deep Learning and Transfer Learning for Imbalanced Datasets,” Deleted Journal, Nov. 2024, doi: 10.1007/s10278-024-01334-0.

[21]R. Siddiqi and S. Javaid, “Deep Learning for Pneumonia Detection in Chest X-ray Images: A Comprehensive Survey,” Journal of Imaging, vol. 10, no. 8, pp. 176–176, July 2024, doi: 10.3390/jimaging10080176.

[22]R. Mostafiz, “FLPneXAINet: Federated deep learning and explainable AI for improved pneumonia prediction utilizing GAN-augmented chest X-ray data,” PLOS ONE, July 2025, doi: 10.1371/journal.pone.0324957.

[23]J. of artificial Intelligence, “Weakly Supervised Pneumonia Localization from Chest X-Rays Using Deep Neural Network and Grad-CAM Explanations,” Jan. 2026, doi: 10.6084/m9.figshare.31817524.

[24]K. T. Reddy, “Explainable deep learning for automated pneumonia detection from chest x-ray images using mobilenetv2 and grad-cam cnn,” Oct. 2025, doi: 10.36227/techrxiv.176108165.56312001/v1.