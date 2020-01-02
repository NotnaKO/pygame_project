for i1 in enemies_group:
    if 0 <= i1.rect.x - self.rect.right < 10:
        self.lefting = True
        i1.righting = True
        self.righting = False
        i1.lefting = False
        if self.coord:
            self.coord = min(self.rect.x - 10, self.coord)
        else:
            self.coord = self.rect.x - 10
        if i1.coord:
            i1.coord = max(i1.rect.x + 1, i1.coord)
        else:
            i1.coord = i1.rect.x + 10
    elif 0 <= self.rect.x - i1.rect.right < 10:
        self.lefting = False
        i1.righting = False
        self.righting = True
        i1.lefting = True
        if i1.coord:

            i1.coord = min(i1.rect.x - 1, i1.coord)
        else:
            i1.coord = i1.rect.x - 10
        if self.coord:
            self.coord = max(self.rect.x + 1, self.coord)
        else:
            self.coord = self.rect.x + 10