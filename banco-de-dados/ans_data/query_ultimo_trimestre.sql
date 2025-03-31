
    SELECT 
        o.razao_social,
        o.registro_ans,
        dc.data_trimestre as trimestre,
        ABS(SUM(dc.valor)) as total_despesa
    FROM 
        demonstracoes_contabeis dc
    JOIN 
        operadoras o ON dc.registro_ans = o.registro_ans
    WHERE 
        dc.descricao_conta LIKE '%EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR%'
        AND dc.data_trimestre = (SELECT MAX(data_trimestre) FROM demonstracoes_contabeis)
    GROUP BY 
        o.razao_social, o.registro_ans
    ORDER BY 
        total_despesa DESC
    LIMIT 10
    