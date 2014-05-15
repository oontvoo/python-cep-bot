package eliza;

import java.util.List;

public class Key
{
    private String key;
    private int rank;
    private List<Decomposition> decompositions;

    public Key(String key, int rank, List<Decomposition> decompositions)
    {
        this.key = key;
        this.rank = rank;
        this.decompositions = decompositions;
    }

    public Key()
    {
        key = null;
        rank = 0;
        decompositions = null;
    }

    public void copyFrom(Key k)
    {
        key = k.keyName();
        rank = k.keyRank();
        decompositions = k.decompositions();
    }

    public String keyName()
    {
        return key;
    }

    public int keyRank()
    {
        return rank;
    }

    public List<Decomposition> decompositions()
    {
        return decompositions;
    }
}
